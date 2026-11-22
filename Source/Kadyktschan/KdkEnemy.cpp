#include "KdkEnemy.h"

#include "AIController.h"
#include "Animation/AnimInstance.h"
#include "Animation/AnimSequence.h"
#include "Components/AudioComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/PointLightComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/SpotLightComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/DamageEvents.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/StaticMesh.h"
#include "Materials/MaterialInterface.h"
#include "Engine/World.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kadyktschan.h"
#include "KdkShooterDirector.h"
#include "Navigation/PathFollowingComponent.h"
#include "Sound/SoundBase.h"

namespace
{
	template <typename T>
	T* Load(const TCHAR* Path) { return LoadObject<T>(nullptr, Path); }

	UPointLightComponent* MakeFlash(AActor* Owner, USceneComponent* Parent, const FVector& At)
	{
		UPointLightComponent* L = NewObject<UPointLightComponent>(Owner);
		L->SetupAttachment(Parent);
		L->SetRelativeLocation(At);
		L->SetIntensityUnits(ELightUnits::Lumens);
		L->SetIntensity(0.f);
		L->SetLightColor(FLinearColor(1.f, 0.7f, 0.35f));
		L->SetAttenuationRadius(900.f);
		L->SetCastShadows(false);
		L->RegisterComponent();
		return L;
	}

	/** Yaw that turns From towards To, degrees. */
	float YawTo(const FVector& From, const FVector& To)
	{
		return (To - From).Rotation().Yaw;
	}
}

AKdkEnemy::AKdkEnemy()
{
	PrimaryActorTick.bCanEverTick = true;
	AIControllerClass = AAIController::StaticClass();
	AutoPossessAI = EAutoPossessAI::Spawned;
	bUseControllerRotationYaw = false;
	GetCharacterMovement()->bOrientRotationToMovement = true;
	GetCharacterMovement()->RotationRate = FRotator(0.f, 300.f, 0.f);
	GetCapsuleComponent()->InitCapsuleSize(26.f, 92.f);  // fits the 24 cm navigation lane through flat doors (DefaultEngine.ini)
	// the player's hit scan and the enemies' line of sight both trace the visibility channel
	GetCapsuleComponent()->SetCollisionResponseToChannel(ECC_Visibility, ECR_Block);
	GetMesh()->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	GetMesh()->SetRelativeLocationAndRotation(FVector(0.f, 0.f, -92.f), FRotator(0.f, -90.f, 0.f));
}

void AKdkEnemy::Init(AKdkShooterDirector* InDirector, const FString& InKind, const FKdkFighter& InTuning, const TArray<FVector>& InPatrol, bool bInGuard)
{
	Director = InDirector;
	Kind = InKind;
	T = InTuning;
	Patrol = InPatrol;
	bGuard = bInGuard;
	Health = T.Health;
	State = bGuard ? EState::Guard : EState::Patrol;
	ThinkIn = FMath::FRand() * 0.2f;  // spread the thinking over frames
	GetCharacterMovement()->MaxWalkSpeed = T.Speed;
	Gun = NewObject<UStaticMeshComponent>(this);
	Gun->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	if (IsMachine())
	{
		// the crawler is the whole mesh; the skeletal mannequin stays empty
		GetCapsuleComponent()->SetCapsuleSize(42.f, 42.f);
		Gun->SetStaticMesh(Load<UStaticMesh>(TEXT("/Game/Kadykchan/Shooter/SM_Shooter_Drone.SM_Shooter_Drone")));
		Gun->SetupAttachment(GetCapsuleComponent());
		Gun->SetRelativeLocation(FVector(0.f, 0.f, -42.f));
		Gun->RegisterComponent();
		Flash = MakeFlash(this, Gun, FVector(64.f, 0.f, 45.f));
		AddHeadlamp(FVector(46.f, -15.f, -12.f));
		Motor = NewObject<UAudioComponent>(this);
		Motor->SetupAttachment(GetCapsuleComponent());
		Motor->SetSound(Load<USoundBase>(TEXT("/Game/Kadykchan/Shooter/Audio/A_DroneMotor_Loop.A_DroneMotor_Loop")));
		Motor->bAllowSpatialization = true;
		Motor->bOverrideAttenuation = true;
		Motor->AttenuationOverrides.FalloffDistance = 3500.f;
		Motor->AttenuationOverrides.AttenuationShapeExtents = FVector(300.f);
		Motor->RegisterComponent();
		Motor->Play();
		return;
	}
	GetMesh()->SetSkeletalMeshAsset(Load<USkeletalMesh>(TEXT("/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple.SKM_Manny_Simple")));
	if (UClass* Anim = LoadClass<UAnimInstance>(nullptr, TEXT("/Game/Characters/Mannequins/Anims/Unarmed/ABP_Unarmed.ABP_Unarmed_C")))
	{
		GetMesh()->SetAnimInstanceClass(Anim);
	}
	Gun->SetStaticMesh(Load<UStaticMesh>(TEXT("/Game/Kadykchan/Shooter/SM_Shooter_Rifle.SM_Shooter_Rifle")));
	Gun->SetupAttachment(GetMesh(), TEXT("hand_r"));
	// shortcut: the rifle hangs from the right hand under an unarmed animation; a rifle anim blueprint comes with real looter models
	Gun->SetRelativeLocationAndRotation(FVector(-2.f, 3.f, 0.f), FRotator(0.f, 90.f, 0.f));
	Gun->RegisterComponent();
	Flash = MakeFlash(this, Gun, FVector(80.f, 0.f, 5.f));
	AddHeadlamp(FVector(14.f, 0.f, 72.f));
}

void AKdkEnemy::AddHeadlamp(const FVector& At)
{
	// miners' head torches from the town's stores: a looter shows where he looks, also at dusk and across the yard
	Lamp = NewObject<USpotLightComponent>(this);
	Lamp->SetupAttachment(GetCapsuleComponent());
	Lamp->SetRelativeLocationAndRotation(At, FRotator(-12.f, 0.f, 0.f));
	Lamp->SetIntensityUnits(ELightUnits::Lumens);
	Lamp->SetIntensity(900.f);
	Lamp->SetLightColor(FLinearColor(1.f, 0.93f, 0.78f));
	Lamp->SetInnerConeAngle(10.f);
	Lamp->SetOuterConeAngle(24.f);
	Lamp->SetAttenuationRadius(2500.f);
	Lamp->SetCastShadows(false);
	Lamp->RegisterComponent();
	Bulb = NewObject<UStaticMeshComponent>(this);
	Bulb->SetStaticMesh(Load<UStaticMesh>(TEXT("/Engine/BasicShapes/Sphere.Sphere")));
	Bulb->SetMaterial(0, Load<UMaterialInterface>(TEXT("/Game/Kadykchan/Materials/M_PowerBulb.M_PowerBulb")));
	Bulb->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	Bulb->SetCastShadow(false);
	Bulb->SetupAttachment(GetCapsuleComponent());
	Bulb->SetRelativeLocation(At);
	Bulb->SetRelativeScale3D(FVector(0.07f));
	Bulb->RegisterComponent();
}

void AKdkEnemy::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	if (Flash && FlashOff > 0.f && (FlashOff -= DeltaSeconds) <= 0.f)
	{
		Flash->SetIntensity(0.f);
	}
	if (State == EState::Dead || !Director.IsValid())
	{
		return;
	}
	if ((ThinkIn -= DeltaSeconds) <= 0.f)
	{
		ThinkIn = 0.2f;
		Think();
	}
	APawn* P = Director->PlayerPawn();
	if (!P || (State != EState::Fight && State != EState::Advance))
	{
		return;
	}
	const float Now = GetWorld()->GetTimeSeconds();
	const float Dist = FVector::Dist(GetActorLocation(), P->GetActorLocation());
	const bool bInSight = Now - LastSeen < 0.3f && SeenFor >= T.React;
	// face the player once it is in sight and close; running to the spot it looks where it runs
	GetCharacterMovement()->bOrientRotationToMovement = !(bInSight && Dist < T.Range * 1.3f);
	if (!GetCharacterMovement()->bOrientRotationToMovement)
	{
		const FRotator Want(0.f, YawTo(GetActorLocation(), P->GetActorLocation()), 0.f);
		SetActorRotation(FMath::RInterpTo(GetActorRotation(), Want, DeltaSeconds, IsMachine() ? 8.f : 6.f));
	}
	// fire only in range, in sight, with a firing right (at most two looters at once); hidden in cover it does not
	if (!bInSight || Dist > T.Range || Now < NextShot || (IsMachine() && Director->IsJammed())
		|| (bCoverSpot && State == EState::Fight && !bPeeking && !IsMachine())
		|| (!IsMachine() && !Director->RequestFireToken(this)))
	{
		return;
	}
	if (ShotsLeft <= 0)
	{
		ShotsLeft = T.Burst;
	}
	// on the run, and the first rounds after spotting the player, go wide
	const float Scale = (GetVelocity().Size2D() > 150.f ? 1.8f : 1.f) * (ShotsSinceSeen < 4 ? 1.7f : 1.f);
	Director->FireAt(this, Muzzle(), T, Scale);
	++ShotsSinceSeen;
	Flash->SetIntensity(9000.f);
	FlashOff = 0.05f;
	NextShot = Now + (--ShotsLeft > 0 ? T.Interval : T.Pause * FMath::FRandRange(0.7f, 1.4f));
}

bool AKdkEnemy::SeesPlayer() const
{
	const APawn* P = Director->PlayerPawn();
	if (!P || (IsMachine() && Director->IsJammed()))
	{
		return false;
	}
	const FVector Eye = GetActorLocation() + FVector(0.f, 0.f, IsMachine() ? 40.f : 70.f);
	const FVector To = P->GetActorLocation() + FVector(0.f, 0.f, 50.f) - Eye;
	const float Dist = To.Size();
	if (Dist > T.Sight)
	{
		return false;
	}
	// a 140 degree view, all round once it is fighting or the player is right behind it
	const bool bInView = State == EState::Fight || State == EState::Advance || Dist < 600.f
		|| FVector::DotProduct(GetActorForwardVector(), To / Dist) > FMath::Cos(FMath::DegreesToRadians(70.f));
	if (!bInView)
	{
		return false;
	}
	FVector Seen;
	return Director->PlayerVisibleFrom(Eye, this, Seen);  // head or chest: behind cover only when peeking
}

bool AKdkEnemy::Reposition(bool bFlank)
{
	const APawn* P = Director->PlayerPawn();
	bool bCover = false;
	if (!P || !Director->FindFightSpot(this, T, bFlank, Spot, Peek, bCover))
	{
		Spot = Peek = GetActorLocation();  // nowhere better: fight from here, stepping sideways
		bCoverSpot = false;
		State = EState::Fight;
		SpotUntil = GetWorld()->GetTimeSeconds() + T.Reposition * 0.5f;
		return false;
	}
	bCoverSpot = bCover;
	bPeeking = false;
	SpotFor = P->GetActorLocation();
	UE_LOG(LogKadyktschan, Display, TEXT("Shooter: %s moves to %s spot %.0f m from the player, %.0f m away%s"), *Kind,
		bCover ? TEXT("cover") : TEXT("open"), FVector::Dist2D(Spot, SpotFor) / 100.f, FVector::Dist2D(Spot, GetActorLocation()) / 100.f,
		bFlank ? TEXT(", flanking") : TEXT(""));
	HitsAtSpot = 0;
	State = EState::Advance;
	StateSince = GetWorld()->GetTimeSeconds();
	MoveTo(Spot, 60.f);
	return true;
}

void AKdkEnemy::Engage()
{
	if (State == EState::Advance || State == EState::Fight)
	{
		return;
	}
	UE_LOG(LogKadyktschan, Display, TEXT("Shooter: %s engages at %.0f m"), *Kind, FVector::Dist(GetActorLocation(), LastKnown) / 100.f);
	ShotsSinceSeen = 0;
	Director->Noise(GetActorLocation(), 2500.f);  // calls out: the ones close by come too
	Reposition(false);
}

void AKdkEnemy::Think()
{
	const float Now = GetWorld()->GetTimeSeconds();
	APawn* P = Director->PlayerPawn();
	if (!P)
	{
		return;
	}
	if (SeesPlayer())
	{
		// noticing takes longer far away: about 2 s at 60 m, half a second up close
		const float Dist = FVector::Dist(GetActorLocation(), P->GetActorLocation());
		SeenFor += 0.2f * (Dist < 1500.f ? 2.f : Dist < 3000.f ? 1.f : 0.5f);
		LastSeen = Now;
		LastKnown = P->GetActorLocation();
		if (SeenFor >= T.React)
		{
			Engage();
		}
	}
	else
	{
		SeenFor = FMath::Max(0.f, SeenFor - 0.1f);
		if (Now - LastSeen > 2.f)
		{
			ShotsSinceSeen = 0;
		}
	}
	const float ToPlayer = FVector::Dist2D(GetActorLocation(), P->GetActorLocation());
	switch (State)
	{
	case EState::Guard:
		if (Now > WaitUntil)  // looks around the flat
		{
			SetActorRotation(FRotator(0.f, GetActorRotation().Yaw + FMath::FRandRange(-120.f, 120.f), 0.f));
			WaitUntil = Now + FMath::FRandRange(3.f, 6.f);
		}
		break;
	case EState::Patrol:
		if (!Patrol.IsEmpty() && !IsMoving() && Now > WaitUntil)
		{
			PatrolIndex = (PatrolIndex + 1) % Patrol.Num();
			MoveTo(Patrol[PatrolIndex]);
			WaitUntil = Now + FMath::FRandRange(2.f, 5.f);  // a pause at every point once it has arrived
		}
		break;
	case EState::Advance:
		if (FVector::Dist2D(GetActorLocation(), Spot) < 150.f || (!IsMoving() && Now - StateSince > 1.f))
		{
			State = EState::Fight;
			StateSince = Now;
			SpotUntil = Now + T.Reposition * FMath::FRandRange(0.8f, 1.3f);
			PhaseUntil = Now + FMath::FRandRange(0.5f, 1.2f);
		}
		else if (FVector::Dist2D(P->GetActorLocation(), SpotFor) > 1200.f)
		{
			Reposition(false);  // the player moved on: the spot no longer fits
		}
		break;
	case EState::Fight:
	{
		if (Now - LastSeen > 6.f)  // lost: go and look where it was seen last
		{
			State = EState::Search;
			StateSince = Now;
			MoveTo(LastKnown, 150.f);
			break;
		}
		// move on: after a while, after two hits, or when the player left the band; then mostly from the side
		if (Now > SpotUntil || HitsAtSpot >= 2 || ToPlayer < T.EngageMin * 0.7f || ToPlayer > T.EngageMax * 1.3f)
		{
			Reposition(FMath::FRand() < 0.7f);
			break;
		}
		if (IsMoving())
		{
			break;
		}
		if (bCoverSpot && Now > PhaseUntil)  // cover: hide a moment, step out to fire, back again
		{
			bPeeking = !bPeeking;
			MoveTo(bPeeking ? Peek : Spot, 30.f);
			PhaseUntil = Now + (bPeeking ? FMath::FRandRange(2.5f, 4.f) : FMath::FRandRange(1.5f, 3.f));
		}
		else if (!bCoverSpot && Now > PhaseUntil)  // open ground: never a standing target, side-steps between bursts
		{
			const FVector Side = FVector::CrossProduct((P->GetActorLocation() - Spot).GetSafeNormal2D(), FVector::UpVector);
			const float Step = IsMachine() ? 450.f : 280.f;
			MoveTo(Spot + Side * FMath::FRandRange(-Step, Step), 40.f);
			PhaseUntil = Now + (IsMachine() ? FMath::FRandRange(0.6f, 1.2f) : FMath::FRandRange(1.2f, 2.5f));
		}
		break;
	}
	case EState::Search:
		if ((!IsMoving() && Now - StateSince > 6.f) || Now - StateSince > 20.f)
		{
			State = bGuard ? EState::Guard : EState::Patrol;
			StateSince = Now;
		}
		else if (!IsMoving() && Now > WaitUntil)  // looks around the last known place
		{
			MoveTo(LastKnown + FVector(FMath::FRandRange(-600.f, 600.f), FMath::FRandRange(-600.f, 600.f), 0.f), 100.f);
			WaitUntil = Now + FMath::FRandRange(1.5f, 3.f);
		}
		break;
	default:
		break;
	}
}

void AKdkEnemy::Hear(const FVector& At)
{
	if (State == EState::Dead || State == EState::Fight || State == EState::Advance)
	{
		return;
	}
	State = EState::Search;
	StateSince = GetWorld()->GetTimeSeconds();
	LastKnown = At + FVector(FMath::FRandRange(-400.f, 400.f), FMath::FRandRange(-400.f, 400.f), 0.f);
	MoveTo(LastKnown, 150.f);
}

void AKdkEnemy::MoveTo(const FVector& At, float Accept)
{
	if (AAIController* AI = Cast<AAIController>(GetController()))
	{
		AI->MoveToLocation(At, Accept, true, true, true, true);
	}
}

bool AKdkEnemy::IsMoving() const
{
	const AAIController* AI = Cast<AAIController>(GetController());
	return AI && AI->GetMoveStatus() == EPathFollowingStatus::Moving;
}

FVector AKdkEnemy::Muzzle() const
{
	return Flash ? Flash->GetComponentLocation() : GetActorLocation() + FVector(0.f, 0.f, 60.f);
}

float AKdkEnemy::TakeDamage(float Damage, FDamageEvent const& Event, AController* Instigator, AActor* Causer)
{
	if (State == EState::Dead)
	{
		return 0.f;
	}
	Health -= Damage;
	if (Health <= 0.f)
	{
		Die();
		return Damage;
	}
	// hit from somewhere: turns to the shooter at once
	if (const APawn* P = Director.IsValid() ? Director->PlayerPawn() : nullptr)
	{
		LastKnown = P->GetActorLocation();
		LastSeen = GetWorld()->GetTimeSeconds();
		SeenFor = FMath::Max(SeenFor, T.React);
		++HitsAtSpot;
		Engage();
	}
	return Damage;
}

void AKdkEnemy::Die()
{
	State = EState::Dead;
	if (AAIController* AI = Cast<AAIController>(GetController()))
	{
		AI->StopMovement();
	}
	GetCapsuleComponent()->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	GetCharacterMovement()->DisableMovement();
	if (Motor)
	{
		Motor->Stop();
	}
	if (Lamp)
	{
		Lamp->SetVisibility(false);
		Bulb->SetVisibility(false);
	}
	if (IsMachine())
	{
		Gun->SetRelativeRotation(FRotator(8.f, 0.f, 14.f));  // tipped over on one track
		Gun->SetRelativeLocation(FVector(0.f, 0.f, -36.f));
	}
	else if (UAnimSequence* Fall = Load<UAnimSequence>(TEXT("/Game/Characters/Mannequins/Anims/Death/MM_Death_Front_01.MM_Death_Front_01")))
	{
		GetMesh()->PlayAnimation(Fall, false);
	}
	if (Director.IsValid())
	{
		Director->OnEnemyDown();
	}
}

AKdkTurret::AKdkTurret()
{
	PrimaryActorTick.bCanEverTick = true;
	Base = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Base"));
	RootComponent = Base;
	Head = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Head"));
	Head->SetupAttachment(Base);
	Head->SetRelativeLocation(FVector(0.f, 0.f, 120.f));
	Lamp = CreateDefaultSubobject<USpotLightComponent>(TEXT("Lamp"));
	Lamp->SetupAttachment(Head);
	Lamp->SetRelativeLocation(FVector(32.f, -18.f, 24.f));
	Lamp->SetIntensityUnits(ELightUnits::Lumens);
	Lamp->SetIntensity(2200.f);
	Lamp->SetLightColor(FLinearColor(1.f, 0.86f, 0.62f));
	Lamp->SetInnerConeAngle(6.f);
	Lamp->SetOuterConeAngle(14.f);
	Lamp->SetAttenuationRadius(7000.f);
	Lamp->SetCastShadows(true);
	Flash = CreateDefaultSubobject<UPointLightComponent>(TEXT("Flash"));
	Flash->SetupAttachment(Head);
	Flash->SetRelativeLocation(FVector(98.f, 0.f, 8.f));
	Flash->SetIntensityUnits(ELightUnits::Lumens);
	Flash->SetIntensity(0.f);
	Flash->SetLightColor(FLinearColor(1.f, 0.7f, 0.35f));
	Flash->SetAttenuationRadius(1000.f);
	Flash->SetCastShadows(false);
}

void AKdkTurret::Init(AKdkShooterDirector* InDirector, const FKdkFighter& InTuning)
{
	Director = InDirector;
	T = InTuning;
	Health = T.Health;
	Base->SetStaticMesh(Load<UStaticMesh>(TEXT("/Game/Kadykchan/Shooter/SM_Shooter_TurretBase.SM_Shooter_TurretBase")));
	Head->SetStaticMesh(Load<UStaticMesh>(TEXT("/Game/Kadykchan/Shooter/SM_Shooter_TurretHead.SM_Shooter_TurretHead")));
	for (UStaticMeshComponent* C : {Base.Get(), Head.Get()})
	{
		C->SetCollisionResponseToChannel(ECC_Visibility, ECR_Block);
	}
	SpinSound = Load<USoundBase>(TEXT("/Game/Kadykchan/Shooter/Audio/A_TurretSpin.A_TurretSpin"));
	SweepYaw = GetActorRotation().Yaw;
}

void AKdkTurret::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	Clock += DeltaSeconds;
	if (FlashOff > 0.f && (FlashOff -= DeltaSeconds) <= 0.f)
	{
		Flash->SetIntensity(0.f);
	}
	const bool bActive = !IsDead() && Director.IsValid() && Director->IsPowerOn() && !Director->IsJammed();
	Lamp->SetVisibility(bActive);
	if (!bActive)
	{
		Head->SetRelativeRotation(FMath::RInterpTo(Head->GetRelativeRotation(), FRotator(-25.f, Head->GetRelativeRotation().Yaw, 0.f), DeltaSeconds, 2.f));
		SpinUntil = -1.f;
		return;
	}
	const APawn* P = Director->PlayerPawn();
	const FVector Pivot = Head->GetComponentLocation();
	bool bSees = false;
	if (P)
	{
		const FVector Target = P->GetActorLocation() + FVector(0.f, 0.f, 40.f);
		const FVector To = Target - Pivot;
		const float Dist = To.Size();
		// sees along its searchlight cone, or all round once it is firing
		const bool bInCone = SpinUntil > 0.f || FVector::DotProduct(Head->GetForwardVector(), To / FMath::Max(Dist, 1.f)) > FMath::Cos(FMath::DegreesToRadians(25.f));
		if (Dist < T.Sight && bInCone)
		{
			FVector Seen;
			bSees = Director->PlayerVisibleFrom(Pivot, this, Seen);
		}
	}
	FRotator Want;
	if (bSees)
	{
		LastSeen = Clock;
		if (SpinUntil < 0.f)
		{
			SpinUntil = Clock + T.React;  // the warning: whine first, then the burst
			Director->PlayAt(SpinSound, Pivot);
			UE_LOG(LogKadyktschan, Display, TEXT("Shooter: turret spins up at %.0f m"), FVector::Dist(Pivot, P->GetActorLocation()) / 100.f);
		}
		Want = (P->GetActorLocation() - Pivot).Rotation() - GetActorRotation();
	}
	else
	{
		if (Clock - LastSeen > 3.f)
		{
			SpinUntil = -1.f;
		}
		// slow sweep of the searchlight across the street
		Want = FRotator(-4.f, SweepYaw - GetActorRotation().Yaw + 60.f * FMath::Sin(Clock * 0.4f), 0.f);
	}
	Head->SetRelativeRotation(FMath::RInterpConstantTo(Head->GetRelativeRotation(), FRotator(Want.Pitch, Want.Yaw, 0.f), DeltaSeconds, bSees ? 70.f : 25.f));
	if (bSees && SpinUntil > 0.f && Clock > SpinUntil && Clock > NextShot)
	{
		if (ShotsLeft <= 0) ShotsLeft = T.Burst;
		Director->FireAt(this, Flash->GetComponentLocation(), T);
		Flash->SetIntensity(12000.f);
		FlashOff = 0.05f;
		NextShot = Clock + (--ShotsLeft > 0 ? T.Interval : T.Pause);
	}
}

float AKdkTurret::TakeDamage(float Damage, FDamageEvent const& Event, AController* Instigator, AActor* Causer)
{
	if (IsDead())
	{
		return 0.f;
	}
	Health -= Damage;
	if (IsDead())
	{
		Lamp->SetVisibility(false);
		Head->SetRelativeRotation(FRotator(-35.f, Head->GetRelativeRotation().Yaw, 12.f));
		if (Director.IsValid()) Director->OnEnemyDown();
	}
	return Damage;
}
