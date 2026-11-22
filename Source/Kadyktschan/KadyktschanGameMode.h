// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "KadyktschanGameMode.generated.h"

/**
 *  Simple GameMode for a first person game
 */
UCLASS(abstract)
class AKadyktschanGameMode : public AGameModeBase
{
	GENERATED_BODY()

public:
	AKadyktschanGameMode();

	/**
	 * Dev hook for run-and-observe evidence (.claude/docs/run-and-observe.md): when the game is started with
	 * -KdkShot=<absolute png path> [-KdkShotDelay=<seconds, default 6>], it waits until the world has settled,
	 * takes a HighResShot to that path and quits. Without the argument it does nothing.
	 * Optional, for checking rooms: -KdkStart=<north m>,<east m>,<yaw> puts the player there,
	 * -KdkWalk=<north>,<east>;... walks those waypoints and logs "KdkWalk: reached/stuck",
	 * -KdkTorch switches the flashlight on, -KdkMap opens the town map,
	 * -KdkShooter[=<seed>] starts a shooter round (-KdkHealth=<0..100> for the camcorder breakdown, -KdkNoEnemies),
	 * -KdkShotUI keeps the overlay in the screenshot.
	 */
	virtual void BeginPlay() override;
	virtual void Tick(float DeltaSeconds) override;

private:
	void TakeEvidenceShot();
	void ApplyDevStart();
	void WalkStep(float DeltaSeconds);

	TArray<FVector2D> WalkPoints;  // UE X/Y in cm
	int32 WalkIndex = 0;
	float WalkStuckTime = 0.f;
	FVector WalkLastPos = FVector::ZeroVector;
	float ShotYaw = TNumericLimits<float>::Max();
	float ShotPitch = 0.f;  // -KdkStart's pitch: kept for the shot (looking at a find on a table)
	bool bWalking = false;
	FTimerHandle StartTimer;

	FString EvidenceShotPath;
};



