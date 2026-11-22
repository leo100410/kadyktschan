// Copyright Epic Games, Inc. All Rights Reserved.

#include "KadyktschanCharacter.h"
#include "Animation/AnimInstance.h"
#include "Camera/CameraComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
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
	for (const FKey& Up : {EKeys::SpaceBar, EKeys::E})
	{
		PlayerInputComponent->BindKey(Up, IE_Pressed, this, &AKadyktschanCharacter::SetVerticalUp);
		PlayerInputComponent->BindKey(Up, IE_Released, this, &AKadyktschanCharacter::SetVerticalNone);
	}
	for (const FKey& Down : {EKeys::C, EKeys::Q})
	{
		PlayerInputComponent->BindKey(Down, IE_Pressed, this, &AKadyktschanCharacter::SetVerticalDown);
		PlayerInputComponent->BindKey(Down, IE_Released, this, &AKadyktschanCharacter::SetVerticalNone);
	}
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
	if (GetController())
	{
		// pass the move inputs
		AddMovementInput(GetActorRightVector(), Right);
		AddMovementInput(GetActorForwardVector(), Forward);
	}
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
}

void AKadyktschanCharacter::ToggleFlight()
{
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
