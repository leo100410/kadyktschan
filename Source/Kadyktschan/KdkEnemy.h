// Shooter mode enemies (design/gdd/shooter-mode.md): looters (UE mannequin with a rifle) and the tracked drone share
// one character with a small state machine - patrol or guard, engage, search, cover. The turret is a fixed actor that
// only runs while the town has power. Tuning per kind from Shooter.json (FKdkFighter).

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "KdkShooter.h"
#include "KdkEnemy.generated.h"

class AKdkShooterDirector;
class UPointLightComponent;
class UStaticMeshComponent;
class USpotLightComponent;
class UAudioComponent;

UCLASS()
class KADYKTSCHAN_API AKdkEnemy : public ACharacter
{
	GENERATED_BODY()

public:
	AKdkEnemy();

	/** Sets the kind ("looter" or "drone"); a guard waits where it stands until it sees or hears the player. */
	void Init(AKdkShooterDirector* InDirector, const FString& InKind, const FKdkFighter& InTuning, const TArray<FVector>& InPatrol, bool bInGuard);

	virtual void Tick(float DeltaSeconds) override;
	virtual float TakeDamage(float Damage, struct FDamageEvent const& Event, AController* Instigator, AActor* Causer) override;

	/** Heard a shot at At (or was sent there as reinforcement): goes to look. */
	void Hear(const FVector& At);
	bool IsDead() const { return State == EState::Dead; }
	bool IsMachine() const { return Kind == TEXT("drone"); }

private:
	// Patrol/Guard: unaware. Advance: running to a fighting spot. Fight: at the spot, hiding and peeking (cover) or
	// side-stepping (open). Search: lost the player, looking where it was. (Design: design/gdd/shooter-mode.md)
	enum class EState : uint8 { Patrol, Guard, Advance, Fight, Search, Dead };

	bool SeesPlayer() const;
	void Think();
	/** Picks a new fighting spot and runs there; false if none (it then fights where it stands). */
	bool Reposition(bool bFlank);
	void Engage();
	void MoveTo(const FVector& At, float Accept = 80.f);
	bool IsMoving() const;
	FVector Muzzle() const;
	void Die();
	void AddHeadlamp(const FVector& At);

	TWeakObjectPtr<AKdkShooterDirector> Director;
	FString Kind;
	FKdkFighter T;
	TArray<FVector> Patrol;
	int32 PatrolIndex = 0;
	bool bGuard = false;
	float Health = 0.f;
	EState State = EState::Patrol;
	float ThinkIn = 0.f;
	float SeenFor = 0.f;
	float LastSeen = -100.f;
	float StateSince = 0.f;
	float WaitUntil = 0.f;
	float NextShot = 0.f;
	int32 ShotsLeft = 0;
	FVector LastKnown = FVector::ZeroVector;
	FVector Spot = FVector::ZeroVector;        // fighting spot (hidden, if it is cover)
	FVector Peek = FVector::ZeroVector;        // where it steps to fire from cover
	FVector SpotFor = FVector::ZeroVector;     // where the player was when the spot was chosen
	bool bCoverSpot = false;
	bool bPeeking = false;
	float PhaseUntil = 0.f;                    // hide/peek or side-step timer
	float SpotUntil = 0.f;                     // time to move on
	int32 HitsAtSpot = 0;
	int32 ShotsSinceSeen = 0;                  // the first rounds after spotting the player go wide

	UPROPERTY() TObjectPtr<UStaticMeshComponent> Gun;      // looter's rifle, or the whole drone
	UPROPERTY() TObjectPtr<UPointLightComponent> Flash;
	UPROPERTY() TObjectPtr<UAudioComponent> Motor;
	UPROPERTY() TObjectPtr<USpotLightComponent> Lamp;
	UPROPERTY() TObjectPtr<UStaticMeshComponent> Bulb;
	float FlashOff = 0.f;
};

UCLASS()
class KADYKTSCHAN_API AKdkTurret : public AActor
{
	GENERATED_BODY()

public:
	AKdkTurret();
	void Init(AKdkShooterDirector* InDirector, const FKdkFighter& InTuning);
	virtual void Tick(float DeltaSeconds) override;
	virtual float TakeDamage(float Damage, struct FDamageEvent const& Event, AController* Instigator, AActor* Causer) override;
	bool IsDead() const { return Health <= 0.f; }

private:
	TWeakObjectPtr<AKdkShooterDirector> Director;
	FKdkFighter T;
	float Health = 0.f;
	float Clock = 0.f;
	float SpinUntil = -1.f;       // spinning up: fires after this
	float LastSeen = -100.f;
	float NextShot = 0.f;
	int32 ShotsLeft = 0;
	float SweepYaw = 0.f;
	float FlashOff = 0.f;

	UPROPERTY() TObjectPtr<UStaticMeshComponent> Base;
	UPROPERTY() TObjectPtr<UStaticMeshComponent> Head;
	UPROPERTY() TObjectPtr<USpotLightComponent> Lamp;
	UPROPERTY() TObjectPtr<UPointLightComponent> Flash;
	UPROPERTY() TObjectPtr<class USoundBase> SpinSound;
};
