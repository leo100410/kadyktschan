// Shooter mode "Einsatz" rules (design/gdd/shooter-mode.md): tuning, the round's tasks and flat pickups, the player's
// health, vest, ammunition and the camcorder breakdown that shows the damage. Plain data + rules, no UObject, so the
// automation tests drive it; loaded from Content/Kadykchan/Data/Shooter.json (tools/research/shooter_data.py).

#pragma once

#include "CoreMinimal.h"

/** One enemy kind (looter, drone, turret); distances in cm, times in seconds, spreads in degrees. */
struct FKdkFighter
{
	float Health = 100.f;
	float Damage = 10.f;
	float Interval = 0.2f;   // between the shots of a burst
	int32 Burst = 3;
	float Pause = 1.f;       // after a burst
	float Spread = 3.f;
	float Range = 5000.f;    // fires from here on
	float Sight = 6000.f;
	float React = 0.7f;      // sees the player this long before the first shot
	float Speed = 300.f;
	float CoverBelow = 0.f;  // health share under which it runs for cover (0: never)
	float EngageMin = 1200.f;  // it fights from this distance band (cm): closer it backs off, farther it advances
	float EngageMax = 2600.f;
	float Reposition = 8.f;    // seconds at one fighting spot before it moves on (flanks)
};

struct FKdkPlayerTuning
{
	float Health = 100.f;
	int32 Mag = 30;
	int32 Reserve = 90;
	float Damage = 40.f;
	float Range = 16000.f;
	float Interval = 0.1f;
	float Spread = 0.6f;     // aimed (right mouse button)
	float SpreadHip = 2.2f;
	float Reload = 2.3f;
	float Fov = 100.f;       // body camera wide angle
	float FovAim = 72.f;
	float Noise = 7000.f;    // enemies this close hear a shot
};

struct FKdkItem
{
	float Heal = 0.f;
	float Armor = 0.f;
	int32 Rounds = 0;
};

/** A furnished flat and the floor points under its ceiling lights (world cm). */
struct FKdkFlat
{
	FString Where;
	FString WhereEn;
	FString Item;            // what its household left behind
	TArray<FVector> Points;
};

struct FKdkTask
{
	FString Id;
	FString Kind;            // fetch_flat, fetch, power_on, jam, destroy
	FString Item;
	FString Mesh;
	FString Goal;
	FString GoalEn;
	FString Done;
	FString DoneEn;
	FVector Pos = FVector::ZeroVector;
	bool bDone = false;
};

struct FKdkPickup
{
	FString Item;
	FVector Pos = FVector::ZeroVector;
	int32 Flat = INDEX_NONE;
	bool bTaken = false;
};

/** A spawn or placement: world cm and yaw in degrees. */
struct FKdkPlaced
{
	FString Mesh;
	FVector Pos = FVector::ZeroVector;
	float Yaw = 0.f;
};

struct KADYKTSCHAN_API FKdkShooter
{
	// data
	FKdkPlayerTuning Player;
	TMap<FString, FKdkFighter> Enemies;
	TMap<FString, FKdkItem> Items;
	TArray<FKdkFlat> Flats;
	TArray<FKdkTask> TaskPool;
	TArray<FKdkPlaced> Starts;  // road exits: start and pick-up points
	TArray<TArray<FVector>> Patrols;
	TArray<FVector> Turrets;
	TArray<FVector> Drones;
	TArray<FKdkPlaced> Obstacles;
	FVector PowerSwitch = FVector::ZeroVector;
	FBox Area = FBox(ForceInit);
	float DistortionExponent = 0.8f;
	float ExtractHold = 30.f;
	float PickupShare = 0.6f;
	float JamTime = 60.f;
	int32 TasksPerRound = 3;
	int32 Reinforcements = 2;
	int32 MaxShooters = 2;
	float TargetFps = 45.f;    // below this the graphics step down automatically during a round     // looters firing at the same time; the others advance or flank
	float SafeStart = 5500.f;  // cm around the start without enemy spawns
	float RegenDelay = 5.f;    // seconds without a hit before health and sight recover
	float HealthRegen = 1.5f;  // health points per second
	float VisionRegen = 12.f;  // sight points per second: the picture clears faster than the wounds heal

	// the round
	float Health = 0.f;
	float Vision = 0.f;         // what the camcorder shows, 0..max health; never below Health, back to it on every hit
	float SinceHit = 0.f;
	float Armor = 0.f;
	int32 Mag = 0;
	int32 Reserve = 0;
	TArray<FKdkTask> Tasks;
	TArray<FKdkPickup> Pickups;
	int32 Current = 0;          // open task; Tasks.Num() once all are done (then: to the pick-up point)
	int32 Start = 0;            // index into Starts
	int32 Extract = 0;

	/** Parses Shooter.json; false when it is malformed or lacks starts, tasks or flats. */
	bool Load(const FString& Json);

	/** Full health and ammunition, TasksPerRound tasks drawn from the pool in a seeded order, PickupShare of the flats
	 *  stocked, start and the pick-up point farthest from it. The same seed gives the same round. */
	void BeginRound(int32 Seed);

	/** A hit: the vest takes 60 % of it while it lasts; the sight drops straight to the health left. Returns it. */
	float Hit(float Damage);

	/** Time passes: after RegenDelay without a hit, health recovers slowly and the sight quickly. */
	void Recover(float DeltaSeconds);
	bool IsDown() const { return Health <= 0.f; }

	/** Camcorder breakdown 0 (intact) .. 1 (down): (1 - vision / max) ^ DistortionExponent. */
	float Distortion() const;

	/** Uses a pickup. False when it is gone or would be wasted (a bandage at full health): it then stays there. */
	bool Take(int32 Pickup);

	/** Spends a round; false with an empty magazine. */
	bool Shoot();
	bool CanReload() const { return Mag < Player.Mag && Reserve > 0; }
	void Reload();

	const FKdkTask* CurrentTask() const { return Tasks.IsValidIndex(Current) ? &Tasks[Current] : nullptr; }
	/** Completes the open task; true when it was the last one. */
	bool CompleteTask();
	bool AllTasksDone() const { return Current >= Tasks.Num(); }
};
