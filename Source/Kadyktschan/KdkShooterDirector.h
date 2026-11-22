// Shooter mode "Einsatz" in the story world (design/gdd/shooter-mode.md): spawns obstacles, pickups, task props, the
// navigation bounds and the enemies at runtime and removes them again, so the story map stays untouched. Runs the
// round (tasks, pick-up point, win/loss), the player's gun and the hits both ways. Rules live in FKdkShooter.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "KdkShooter.h"
#include "KdkShooterDirector.generated.h"

class AKadyktschanPlayerController;
class AKadyktschanCharacter;
class UStaticMeshComponent;
class USoundBase;
class USoundAttenuation;

/** What the overlay shows in the shooter mode: world positions, the controller projects them. */
struct FKdkShooterHud
{
	FString Header;
	FString Goal;
	FString Prompt;                // "[E] ..." or a short message
	bool bFocus = false;           // Prompt belongs to a thing in view
	FVector Focus = FVector::ZeroVector;
	bool bMarker = false;
	FVector Target = FVector::ZeroVector;
	TArray<FVector> Rings;         // looters marked by the situation map
	float Spread = 0.f;            // current shot spread, degrees (crosshair size)
	float Health = 1.f;            // share of max health (red aura)
	TArray<FVector4f> Threats;     // where shots came from: world x, y, z and strength 0..1 (fading)
	TArray<FVector4f> Marks;       // enemies that hit the player in the last 2 s: above the head, alpha (fading)
	float HitMarker = 0.f;         // 1 right after a hit, fading to 0
	bool bKill = false;            // the last hit took the enemy down
};

UCLASS()
class KADYKTSCHAN_API AKdkShooterDirector : public AActor
{
	GENERATED_BODY()

public:
	AKdkShooterDirector();

	/** Loads Shooter.json, places everything and puts the player at the start; false when the data is missing. */
	bool BeginRound(AKadyktschanPlayerController* InPlayer, int32 Seed);

	/** Removes everything the round spawned (also on Destroyed). */
	void EndRound();

	virtual void Tick(float DeltaSeconds) override;
	virtual void Destroyed() override;

	// player input
	void SetFiring(bool bOn) { bFiring = bOn; }
	void SetAiming(bool bOn);
	void Reload();
	/** E: takes the pickup or works the task prop in view. True when E was used here (else: close the result panel). */
	bool Interact();

	void FillHud(FKdkShooterHud& Out) const;
	bool IsOver() const { return Phase == EPhase::Over; }
	bool IsPowerOn() const { return bPower; }
	bool IsJammed() const;
	float Distortion() const { return Rules.Distortion(); }
	APawn* PlayerPawn() const;

	// enemies
	/** The player's head (the camera, also when it peeks out of cover) or chest seen from Eye, if either is in
	 *  sight; OutTarget is the visible one. Behind cover with the camera down, neither is. */
	bool PlayerVisibleFrom(const FVector& Eye, const AActor* Ignore, FVector& OutTarget) const;
	/** One enemy round at the player from Muzzle; spread grows with distance and the player's speed, times
	 *  SpreadScale (firing on the move, the first shots). */
	void FireAt(AActor* Shooter, const FVector& Muzzle, const FKdkFighter& Tuning, float SpreadScale = 1.f);

	/** A place for an enemy to fight from, inside its distance band around the player: preferably the far side of
	 *  an obstacle (hidden from the player) with a peek point beside it, else open ground with a clear view.
	 *  bFlank prefers spots off its current line to the player; spots near other enemies' count against. */
	bool FindFightSpot(const AActor* Enemy, const FKdkFighter& Tuning, bool bFlank, FVector& OutSpot, FVector& OutPeek, bool& bOutCover);

	/** At most MaxShooters looters fire at the same time; a granted right lasts 2.5 s and is renewed by firing. */
	bool RequestFireToken(const AActor* Shooter);
	/** A shot or an explosion the enemies within Radius hear. */
	void Noise(const FVector& At, float Radius);
	void OnEnemyDown();
	/** A short message under the view centre for 4 s. */
	void Toast(const FString& De, const FString& En);
	/** A sound in the street: spatialised, fades out over about 80 m. */
	void PlayAt(USoundBase* Sound, const FVector& At, float Volume = 1.f) const;
	/** Cover spot behind the nearest obstacle as seen from the player, within MaxDist of From; false if none. */
	bool FindCover(const FVector& From, float MaxDist, FVector& Out) const;

	FKdkShooter Rules;

private:
	enum class EPhase : uint8 { Loading, Running, Over };

	/** A mesh from /Game/Kadykchan/Shooter, dropped onto what lies below Pos + Up cm (Up < 0: exactly at Pos). */
	UStaticMeshComponent* Place(const FString& Mesh, const FVector& Pos, float Yaw, float Up, float Scale = 1.f);
	void SpawnNavigation();
	void SpawnEnemies();
	void SpawnLooter(const FVector& At, const TArray<FVector>& Patrol, bool bGuard, bool bAlert);
	void SpawnDrone(const FVector& At);
	void Reinforce(int32 Looters, int32 Drones);
	void ShootOnce();
	/** Spread of the next shot in degrees: tight aimed, wide from the hip, worse while moving. */
	float PlayerSpread() const;
	void DamagePlayer(float Damage);
	void Finish(bool bWon);
	FVector Ground(const FVector& Pos, float Up) const;
	void CompleteTask();
	bool bEnded = false;

	TWeakObjectPtr<AKadyktschanPlayerController> Player;
	UPROPERTY() TArray<TObjectPtr<UStaticMeshComponent>> Placed;
	UPROPERTY() TArray<TObjectPtr<AActor>> Spawned;
	UPROPERTY() TArray<TObjectPtr<UStaticMeshComponent>> PickupMeshes;   // by pickup index
	UPROPERTY() TArray<TObjectPtr<UStaticMeshComponent>> TaskMeshes;     // by task index (null: no prop)
	UPROPERTY() TObjectPtr<USoundBase> ShotSound;
	UPROPERTY() TObjectPtr<USoundBase> ShotFarSound;
	UPROPERTY() TObjectPtr<USoundBase> ImpactSound;
	UPROPERTY() TObjectPtr<USoundBase> GlitchSound;
	UPROPERTY() TObjectPtr<USoundBase> ClickSound;
	UPROPERTY() TObjectPtr<USoundAttenuation> Attenuation;
	TArray<FVector> CoverSpots;   // obstacle centres

	EPhase Phase = EPhase::Loading;
	float Clock = 0.f;            // round time, seconds (pause-aware: actor tick)
	float LoadTime = 0.f;
	bool bFiring = false;
	bool bAiming = false;
	float NextShot = 0.f;
	float ReloadDone = -1.f;
	bool bPower = false;
	float JamUntil = -1.f;
	bool bIntel = false;
	bool bWorkshopDown = false;
	bool bHoldWave = false;
	float HoldLeft = 0.f;
	float ToastUntil = -1.f;
	FString ToastText;
	int32 Kills = 0;
	float HitMarkUntil = -1.f;
	struct FThreat { FVector From; float Time; float Strength; };
	TMap<TWeakObjectPtr<const AActor>, FVector> Claims;            // fighting spots taken
	TMap<TWeakObjectPtr<AActor>, float> HitBy;                     // who hit the player, when (marked for 2 s)
	TArray<TPair<TWeakObjectPtr<const AActor>, float>> FireTokens;  // who may fire, until when
	TArray<FThreat> Threats;
	bool bKillMark = false;
	int32 HitsTaken = 0;
	// focus of E: pickup index, task, or the power switch
	enum class EFocus : uint8 { None, Pickup, Task, Switch } FocusKind = EFocus::None;
	int32 FocusPickup = INDEX_NONE;
	FVector FocusPos = FVector::ZeroVector;
	// what the round changed on the player, restored by EndRound
	FVector SavedLocation = FVector::ZeroVector;
	FRotator SavedRotation = FRotator::ZeroRotator;
	TEnumAsByte<ECollisionResponse> SavedVisibility = ECR_Ignore;
};
