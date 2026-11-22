// Copyright Epic Games, Inc. All Rights Reserved.

#include "KadyktschanCharacter.h"
#include "Animation/AnimInstance.h"
#include "Camera/CameraComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/PointLightComponent.h"
#include "Components/SpotLightComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "KadyktschanCameraManager.h"
#include "GameFramework/PlayerController.h"
#include "EnhancedInputComponent.h"
#include "InputActionValue.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kadyktschan.h"
#include "KdkGameUserSettings.h"

AKadyktschanCharacter::AKadyktschanCharacter()
{
	// Set size for collision capsule
	GetCapsuleComponent()->InitCapsuleSize(55.f, 96.0f);
	
	// Create the first person mesh that will be viewed only by this character's owner
	FirstPersonMesh = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("First Person Mesh"));

	FirstPersonMesh->SetupAttachment(GetMesh());
	FirstPersonMesh->SetOnlyOwnerSee(true);
	FirstPersonMesh->FirstPersonPrimitiveType = EFirstPersonPrimitiveType::FirstPerson;
	FirstPersonMesh->SetCollisionProfileName(FName("NoCollision"));

	// Create the Camera Component	
	FirstPersonCameraComponent = CreateDefaultSubobject<UCameraComponent>(TEXT("First Person Camera"));
	FirstPersonCameraComponent->SetupAttachment(FirstPersonMesh, FName("head"));
	FirstPersonCameraComponent->SetRelativeLocationAndRotation(FVector(-2.8f, 5.89f, 0.0f), FRotator(0.0f, 90.0f, -90.0f));
	FirstPersonCameraComponent->bUsePawnControlRotation = true;
	FirstPersonCameraComponent->bEnableFirstPersonFieldOfView = true;
	FirstPersonCameraComponent->bEnableFirstPersonScale = true;
	FirstPersonCameraComponent->FirstPersonFieldOfView = 70.0f;
	FirstPersonCameraComponent->FirstPersonScale = 0.6f;

	// flashlight held a little right of and below the eyes, so its shadows read as coming from the hand
	Flashlight = CreateDefaultSubobject<USpotLightComponent>(TEXT("Flashlight"));
	Flashlight->SetupAttachment(FirstPersonCameraComponent);
	Flashlight->SetRelativeLocation(FVector(10.f, 18.f, -14.f));
	Flashlight->SetIntensityUnits(ELightUnits::Lumens);
	Flashlight->SetIntensity(220.f);  // 800 lm still glared white indoors once auto exposure adapted (user, 2026-11-08)
	Flashlight->SetLightColor(FLinearColor(1.f, 0.74f, 0.42f));  // old Soviet torch bulb with a weak battery, yellowish
	Flashlight->SetInnerConeAngle(16.f);
	Flashlight->SetOuterConeAngle(40.f);
	Flashlight->SetAttenuationRadius(2500.f);
	Flashlight->SetCastShadows(true);
	Flashlight->SetVisibility(false);

	// shooter mode rifle: rendered as a first-person primitive (own FOV, never clips into walls), hidden in the story
	Rifle = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Rifle"));
	Rifle->SetupAttachment(FirstPersonCameraComponent);
	Rifle->SetOnlyOwnerSee(true);
	Rifle->FirstPersonPrimitiveType = EFirstPersonPrimitiveType::FirstPerson;
	Rifle->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	Rifle->SetCastShadow(false);
	Rifle->SetVisibility(false);
	MuzzleFlash = CreateDefaultSubobject<UPointLightComponent>(TEXT("MuzzleFlash"));
	MuzzleFlash->SetupAttachment(Rifle);
	MuzzleFlash->SetRelativeLocation(FVector(82.f, 0.f, 5.f));
	MuzzleFlash->SetIntensityUnits(ELightUnits::Lumens);
	MuzzleFlash->SetIntensity(0.f);
	MuzzleFlash->SetLightColor(FLinearColor(1.f, 0.7f, 0.35f));
	MuzzleFlash->SetAttenuationRadius(1200.f);
	MuzzleFlash->SetCastShadows(false);
	GetCharacterMovement()->NavAgentProps.bCanCrouch = true;
	GetCharacterMovement()->SetCrouchedHalfHeight(58.f);

	// configure the character comps
	GetMesh()->SetOwnerNoSee(true);
	GetMesh()->FirstPersonPrimitiveType = EFirstPersonPrimitiveType::WorldSpaceRepresentation;

	GetCapsuleComponent()->SetCapsuleSize(34.0f, 96.0f);

	// Configure character movement
	GetCharacterMovement()->BrakingDecelerationFalling = 1500.0f;
	GetCharacterMovement()->AirControl = 0.5f;
}

void AKadyktschanCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{	
	// Set up action bindings
	if (UEnhancedInputComponent* EnhancedInputComponent = Cast<UEnhancedInputComponent>(PlayerInputComponent))
	{
		// Jumping
		EnhancedInputComponent->BindAction(JumpAction, ETriggerEvent::Started, this, &AKadyktschanCharacter::DoJumpStart);
		EnhancedInputComponent->BindAction(JumpAction, ETriggerEvent::Completed, this, &AKadyktschanCharacter::DoJumpEnd);

		// Moving
		EnhancedInputComponent->BindAction(MoveAction, ETriggerEvent::Triggered, this, &AKadyktschanCharacter::MoveInput);

		// Looking/Aiming
		EnhancedInputComponent->BindAction(LookAction, ETriggerEvent::Triggered, this, &AKadyktschanCharacter::LookInput);
		EnhancedInputComponent->BindAction(MouseLookAction, ETriggerEvent::Triggered, this, &AKadyktschanCharacter::LookInput);
	}
	else
	{
		UE_LOG(LogKadyktschan, Error, TEXT("'%s' Failed to find an Enhanced Input Component! This template is built to use the Enhanced Input system. If you intend to use the legacy system, then you will need to update this C++ file."), *GetNameSafe(this));
	}
	// flight keys are plain key bindings: a viewing aid, not part of the designed input map
	PlayerInputComponent->BindKey(EKeys::F, IE_Pressed, this, &AKadyktschanCharacter::ToggleFlight);
	PlayerInputComponent->BindKey(EKeys::L, IE_Pressed, this, &AKadyktschanCharacter::ToggleFlashlight);
	for (const FKey& Up : {EKeys::SpaceBar})  // E reads finds (player controller)
	{
		PlayerInputComponent->BindKey(Up, IE_Pressed, this, &AKadyktschanCharacter::SetVerticalUp);
		PlayerInputComponent->BindKey(Up, IE_Released, this, &AKadyktschanCharacter::SetVerticalNone);
	}
	PlayerInputComponent->BindKey(EKeys::C, IE_Pressed, this, &AKadyktschanCharacter::SetVerticalDown);
	PlayerInputComponent->BindKey(EKeys::C, IE_Released, this, &AKadyktschanCharacter::SetVerticalNone);
	PlayerInputComponent->BindKey(EKeys::Q, IE_Pressed, this, &AKadyktschanCharacter::QPressed);  // shooter: cover
	PlayerInputComponent->BindKey(EKeys::Q, IE_Released, this, &AKadyktschanCharacter::QReleased);
	PlayerInputComponent->BindKey(EKeys::LeftControl, IE_Pressed, this, &AKadyktschanCharacter::ToggleCrouch);  // shooter mode only
	PlayerInputComponent->BindKey(EKeys::LeftShift, IE_Pressed, this, &AKadyktschanCharacter::BoostOn);
	PlayerInputComponent->BindKey(EKeys::LeftShift, IE_Released, this, &AKadyktschanCharacter::BoostOff);
	PlayerInputComponent->BindKey(EKeys::MouseScrollUp, IE_Pressed, this, &AKadyktschanCharacter::FlyFaster);
	PlayerInputComponent->BindKey(EKeys::MouseScrollDown, IE_Pressed, this, &AKadyktschanCharacter::FlySlower);
}


void AKadyktschanCharacter::MoveInput(const FInputActionValue& Value)
{
	// get the Vector2D move axis
	FVector2D MovementVector = Value.Get<FVector2D>();

	// pass the axis values to the move input
	DoMove(MovementVector.X, MovementVector.Y);

}

void AKadyktschanCharacter::LookInput(const FInputActionValue& Value)
{
	// get the Vector2D look axis
	FVector2D LookAxisVector = Value.Get<FVector2D>();

	// pass the axis values to the aim input
	DoAim(LookAxisVector.X, LookAxisVector.Y);

}

void AKadyktschanCharacter::DoAim(float Yaw, float Pitch)
{
	if (GetController())
	{
		if (const UKdkGameUserSettings* Settings = UKdkGameUserSettings::Get())
		{
			Yaw *= Settings->MouseSensitivity;
			Pitch *= Settings->MouseSensitivity * (Settings->bInvertMouseY ? -1.f : 1.f);
		}
		// pass the rotation inputs
		AddControllerYawInput(Yaw);
		AddControllerPitchInput(Pitch);
	}
}

void AKadyktschanCharacter::DoMove(float Right, float Forward)
{
	if (bFlying && GetController())
	{
		const FRotator View = GetControlRotation();  // fly where the camera looks, pitch included
		AddMovementInput(FRotationMatrix(View).GetUnitAxis(EAxis::X), Forward);
		AddMovementInput(FRotationMatrix(View).GetUnitAxis(EAxis::Y), Right);
		return;
	}
	if (bInCover && GetController())
	{
		// in cover only along it; a clear step away from the cover leaves it
		const FRotator Yaw(0.f, GetControlRotation().Yaw, 0.f);
		const FVector Wish = FRotationMatrix(Yaw).GetUnitAxis(EAxis::X) * Forward + FRotationMatrix(Yaw).GetUnitAxis(EAxis::Y) * Right;
		if (FVector::DotProduct(Wish, CoverNormal) > 0.7f)
		{
			LeaveCover();
		}
		else
		{
			const FVector Along = FVector::CrossProduct(FVector::UpVector, CoverNormal);
			const float A = FVector::DotProduct(Wish, Along);
			FHitResult Hit;
			// stop at the end of the cover instead of sliding out into the open
			if (FMath::Abs(A) > 0.1f && HasCoverAt(GetActorLocation() + Along * FMath::Sign(A) * 45.f, 60.f, Hit))
			{
				AddMovementInput(Along * FMath::Sign(A), FMath::Abs(A));
			}
			return;
		}
	}
	if (GetController())
	{
		// pass the move inputs
		AddMovementInput(GetActorRightVector(), Right);
		AddMovementInput(GetActorForwardVector(), Forward);
	}
}

bool AKadyktschanCharacter::HasCoverAt(const FVector& At, float Reach, FHitResult& OutHit) const
{
	// 35, 55 and 80 cm above the feet (also when crouched), towards the cover; walls only (not a slope or a step).
	// Several heights: a stack of slabs on timber bearers has gaps a single ray slips through (cover lost, 2026-11-11)
	const float Feet = At.Z - GetCapsuleComponent()->GetScaledCapsuleHalfHeight();
	FCollisionQueryParams Params(SCENE_QUERY_STAT(KdkCover), false, this);
	for (const float Height : {55.f, 35.f, 80.f})
	{
		const FVector From(At.X, At.Y, Feet + Height);
		if (GetWorld()->LineTraceSingleByChannel(OutHit, From, From - CoverNormal * (GetCapsuleComponent()->GetScaledCapsuleRadius() + Reach),
			ECC_Visibility, Params) && FMath::Abs(OutHit.ImpactNormal.Z) < 0.3f)
		{
			return true;
		}
	}
	return false;
}

void AKadyktschanCharacter::QPressed()
{
	if (!bShooter)
	{
		SetVerticalDown();
		return;
	}
	if (bInCover)
	{
		LeaveCover();
	}
	else
	{
		EnterCover();
	}
}

void AKadyktschanCharacter::EnterCover()
{
	// the nearest wall within 1.6 m, looking ahead first, then to the sides and behind
	const FVector View = FRotationMatrix(FRotator(0.f, GetControlRotation().Yaw, 0.f)).GetUnitAxis(EAxis::X);
	for (const float Turn : {0.f, -45.f, 45.f, -90.f, 90.f, -135.f, 135.f, 180.f})
	{
		CoverNormal = -View.RotateAngleAxis(Turn, FVector::UpVector);
		FHitResult Hit;
		if (!HasCoverAt(GetActorLocation(), 130.f, Hit))
		{
			continue;
		}
		CoverNormal = FVector(Hit.ImpactNormal.X, Hit.ImpactNormal.Y, 0.f).GetSafeNormal();
		// the top of the cover, a hand's breadth behind its face; above standing eye height it is a wall
		const FVector Inside = Hit.ImpactPoint - CoverNormal * 12.f;
		const float Feet = GetActorLocation().Z - GetCapsuleComponent()->GetScaledCapsuleHalfHeight();
		FHitResult Top;
		FCollisionQueryParams Params(SCENE_QUERY_STAT(KdkCoverTop), false, this);
		CoverTop = GetWorld()->LineTraceSingleByChannel(Top, FVector(Inside.X, Inside.Y, Feet + 260.f), FVector(Inside.X, Inside.Y, Feet), ECC_Visibility, Params)
			? Top.ImpactPoint.Z : Feet + 260.f;
		bLowCover = CoverTop - Feet < 155.f;
		CoverTarget = FVector(Hit.ImpactPoint.X, Hit.ImpactPoint.Y, GetActorLocation().Z) + CoverNormal * (GetCapsuleComponent()->GetScaledCapsuleRadius() + 6.f);
		CoverSnap = 0.2f;
		bInCover = true;
		Crouch();  // low cover: the camera goes below its edge; at a wall crouching keeps the chest out of windows
		UE_LOG(LogKadyktschan, Display, TEXT("Shooter: cover %s, %.0f cm high, %.0f cm away"), bLowCover ? TEXT("low") : TEXT("high"),
			CoverTop - Feet, Hit.Distance);
		return;
	}
	UE_LOG(LogKadyktschan, Display, TEXT("Shooter: no cover within reach"));
}

void AKadyktschanCharacter::LeaveCover()
{
	if (bInCover)
	{
		UnCrouch();
	}
	bInCover = false;
}

void AKadyktschanCharacter::UpdateCover(float DeltaSeconds)
{
	FVector Want = FVector::ZeroVector;  // where the camera should sit relative to the body, world space
	if (bInCover && CoverSnap > 0.f)  // slide against the cover
	{
		const float Alpha = FMath::Min(1.f, DeltaSeconds / CoverSnap);
		CoverSnap -= DeltaSeconds;
		SetActorLocation(FMath::Lerp(GetActorLocation(), FVector(CoverTarget.X, CoverTarget.Y, GetActorLocation().Z), Alpha), true);
	}
	else if (bInCover)
	{
		FHitResult Hit;
		if (!HasCoverAt(GetActorLocation(), 60.f, Hit))  // pushed away or the cover is gone
		{
			UE_LOG(LogKadyktschan, Display, TEXT("Shooter: cover lost (hit %d, %s, normal %s, half height %.0f, at %s)"), Hit.bBlockingHit,
				*GetNameSafe(Hit.GetComponent()), *Hit.ImpactNormal.ToString(), GetCapsuleComponent()->GetScaledCapsuleHalfHeight(), *GetActorLocation().ToString());
			LeaveCover();
		}
	}
	if (bInCover)
	{
		const float Eye = FirstPersonCameraComponent->GetComponentLocation().Z - EyeOffset.Z;
		if (bLowCover)
		{
			// hidden: the lens a little below the edge; aiming: just over it, like peeking over a wall
			Want.Z = FMath::Clamp((bAiming ? CoverTop + 18.f : CoverTop - 28.f) - Eye, -90.f, 70.f);
		}
		else if (bAiming)
		{
			// at a wall: lean out past the nearer free edge (the side the view points to first)
			const FVector Along = FVector::CrossProduct(FVector::UpVector, CoverNormal);
			const float Prefer = FVector::DotProduct(GetControlRotation().Vector(), Along) >= 0.f ? 1.f : -1.f;
			FHitResult Hit;
			for (const float Side : {Prefer, -Prefer})
			{
				if (!HasCoverAt(GetActorLocation() + Along * Side * 75.f, 60.f, Hit))
				{
					Want = Along * Side * 65.f;
					Want.Z = GetCapsuleComponent()->GetUnscaledCapsuleHalfHeight() > 70.f ? 0.f : 25.f;  // rise a bit out of the crouch
					break;
				}
			}
		}
	}
	EyeOffset = FMath::VInterpTo(EyeOffset, Want, DeltaSeconds, 12.f);
	// the camera and the rifle hang on the first person mesh: moving it moves both, so the rifle stays in view
	FirstPersonMesh->SetRelativeLocation(FirstPersonBase + GetMesh()->GetComponentTransform().InverseTransformVectorNoScale(EyeOffset));
}

void AKadyktschanCharacter::DoJumpStart()
{
	// pass Jump to the character
	Jump();
}

void AKadyktschanCharacter::DoJumpEnd()
{
	// pass StopJumping to the character
	StopJumping();
}

void AKadyktschanCharacter::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	if (bFlying && VerticalInput != 0.f)
	{
		AddMovementInput(FVector::UpVector, VerticalInput);
	}
	if (bShooter)
	{
		UpdateRifle(DeltaSeconds);
		UpdateCover(DeltaSeconds);
	}
}

void AKadyktschanCharacter::SetShooterMode(bool bOn, float Fov)
{
	if (bOn == bShooter)
	{
		return;
	}
	bShooter = bOn;
	if (bOn && bFlying)
	{
		ToggleFlight();
	}
	if (bOn)
	{
		StoryFov = FirstPersonCameraComponent->FieldOfView;
		FirstPersonBase = FirstPersonMesh->GetRelativeLocation();
		EyeOffset = FVector::ZeroVector;
		StoryWalkSpeed = GetCharacterMovement()->MaxWalkSpeed;
		if (!Rifle->GetStaticMesh())
		{
			Rifle->SetStaticMesh(LoadObject<UStaticMesh>(nullptr, TEXT("/Game/Kadykchan/Shooter/SM_Shooter_Rifle.SM_Shooter_Rifle")));
		}
		TargetFov = Fov;
		LastView = GetControlRotation();
	}
	else
	{
		UnCrouch();
		FirstPersonCameraComponent->SetFieldOfView(StoryFov);
		FirstPersonMesh->SetRelativeLocation(FirstPersonBase);
		GetCharacterMovement()->MaxWalkSpeed = StoryWalkSpeed;
		bAiming = bReloading = bInCover = false;
	}
	Rifle->SetVisibility(bOn);
	MuzzleFlash->SetIntensity(0.f);
	ApplyWalkSpeed();
	if (const APlayerController* PC = Cast<APlayerController>(GetController()))
	{
		if (AKadyktschanCameraManager* Cam = Cast<AKadyktschanCameraManager>(PC->PlayerCameraManager))
		{
			Cam->Handheld = bOn ? 1.f : 0.f;
		}
	}
}

void AKadyktschanCharacter::ApplyWalkSpeed()
{
	if (bShooter)
	{
		GetCharacterMovement()->MaxWalkSpeed = bBoost ? 620.f : 380.f;
		GetCharacterMovement()->MaxWalkSpeedCrouched = 200.f;
	}
}

void AKadyktschanCharacter::ToggleCrouch()
{
	if (!bShooter)
	{
		return;
	}
	if (bIsCrouched)
	{
		UnCrouch();
	}
	else
	{
		Crouch();
	}
}

void AKadyktschanCharacter::ShotFx()
{
	Kick = FMath::Min(1.f, Kick + 0.45f);
	FlashLeft = 0.045f;
	MuzzleFlash->SetIntensity(14000.f);
}

void AKadyktschanCharacter::UpdateRifle(float DeltaSeconds)
{
	UCameraComponent* Cam = FirstPersonCameraComponent;
	Cam->SetFieldOfView(FMath::FInterpTo(Cam->FieldOfView, TargetFov, DeltaSeconds, 10.f));
	Aim = FMath::FInterpTo(Aim, bAiming && !bReloading ? 1.f : 0.f, DeltaSeconds, 12.f);
	ReloadPose = FMath::FInterpTo(ReloadPose, bReloading ? 1.f : 0.f, DeltaSeconds, 8.f);
	Kick = FMath::FInterpTo(Kick, 0.f, DeltaSeconds, 14.f);
	if (FlashLeft > 0.f && (FlashLeft -= DeltaSeconds) <= 0.f)
	{
		MuzzleFlash->SetIntensity(0.f);
	}
	// the rifle lags behind fast turns (camera space: x forward, y right, z up)
	const FRotator View = GetControlRotation();
	const FRotator Delta = (View - LastView).GetNormalized();
	LastView = View;
	const FRotator Want(FMath::Clamp(-Delta.Pitch * 1.6f, -4.f, 4.f), FMath::Clamp(-Delta.Yaw * 1.6f, -5.f, 5.f), 0.f);
	Sway = FMath::RInterpTo(Sway, Want, DeltaSeconds, 9.f);
	const float Speed = GetVelocity().Size2D() / 600.f;
	const float Step = GetWorld()->GetTimeSeconds() * 9.f;
	const FVector Hip(46.f, 15.f, -23.f), Sights(22.f, 0.f, -9.3f);
	FVector Loc = FMath::Lerp(Hip, Sights, Aim) + FVector(-Kick * 5.f, 0.f, FMath::Sin(Step * 2.f) * 0.5f * Speed * (1.f - Aim))
		+ FVector(0.f, FMath::Sin(Step) * 0.7f * Speed, 0.f) + FVector(0.f, 0.f, -10.f) * ReloadPose;
	const FRotator Rot = Sway * (1.f - 0.6f * Aim) + FRotator(Kick * 3.f, 0.f, 0.f) + FRotator(-35.f, 10.f, 25.f) * ReloadPose;
	Rifle->SetRelativeLocationAndRotation(Loc, Rot);
	if (const APlayerController* PC = Cast<APlayerController>(GetController()))
	{
		if (AKadyktschanCameraManager* CamManager = Cast<AKadyktschanCameraManager>(PC->PlayerCameraManager))
		{
			CamManager->WalkSpeed01 = FMath::Clamp(Speed, 0.f, 1.f) * (GetCharacterMovement()->IsMovingOnGround() ? 1.f : 0.f);
		}
	}
}

void AKadyktschanCharacter::ToggleFlashlight()
{
	Flashlight->SetVisibility(!Flashlight->IsVisible());
}

void AKadyktschanCharacter::ToggleFlight()
{
	if (bShooter && !bFlying)  // the viewing aid is for the story world; no flying over the enemies
	{
		return;
	}
	UCharacterMovementComponent* Move = GetCharacterMovement();
	bFlying = !bFlying;
	SetActorEnableCollision(!bFlying);  // fly through buildings and terrain
	if (bFlying)
	{
		Move->SetMovementMode(MOVE_Flying);
		Move->BrakingDecelerationFlying = 6000.f;
		ApplyFlySpeed();
	}
	else
	{
		VerticalInput = 0.f;
		Move->SetMovementMode(MOVE_Falling);
	}
}

void AKadyktschanCharacter::ChangeFlySpeed(float Factor)
{
	FlySpeed = FMath::Clamp(FlySpeed * Factor, 300.f, 20000.f);
	ApplyFlySpeed();
}

void AKadyktschanCharacter::ApplyFlySpeed()
{
	GetCharacterMovement()->MaxFlySpeed = FlySpeed * (bBoost ? FlyBoost : 1.f);
	GetCharacterMovement()->MaxAcceleration = FMath::Max(2048.f, GetCharacterMovement()->MaxFlySpeed * 4.f);
}
