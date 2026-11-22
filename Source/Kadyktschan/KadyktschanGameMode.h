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
	 */
	virtual void BeginPlay() override;

private:
	void TakeEvidenceShot();

	FString EvidenceShotPath;
	FTimerHandle EvidenceTimer;
	FTimerHandle QuitTimer;
};



