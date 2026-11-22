// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Camera/PlayerCameraManager.h"
#include "KadyktschanCameraManager.generated.h"

/**
 *  Basic First Person camera manager.
 *  Limits min/max look pitch.
 */
UCLASS()
class AKadyktschanCameraManager : public APlayerCameraManager
{
	GENERATED_BODY()
	
public:

	/** Constructor */
	AKadyktschanCameraManager();

	/** Shooter mode body camera: handheld wobble strength (0 in the story) and walking 0..1, set by the character. */
	float Handheld = 0.f;
	float WalkSpeed01 = 0.f;

	/** A hit: the picture jolts, decaying over about half a second. */
	void Jolt(float Strength) { JoltLeft = FMath::Max(JoltLeft, Strength); }

protected:
	virtual void UpdateViewTarget(FTViewTarget& OutVT, float DeltaTime) override;

private:
	float Time = 0.f;
	float BobPhase = 0.f;
	float JoltLeft = 0.f;
};
