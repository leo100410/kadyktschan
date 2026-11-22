// Copyright Epic Games, Inc. All Rights Reserved.


#include "KadyktschanCameraManager.h"

AKadyktschanCameraManager::AKadyktschanCameraManager()
{
	// set the min/max pitch
	ViewPitchMin = -70.0f;
	ViewPitchMax = 80.0f;
}

void AKadyktschanCameraManager::UpdateViewTarget(FTViewTarget& OutVT, float DeltaTime)
{
	Super::UpdateViewTarget(OutVT, DeltaTime);
	if (Handheld <= 0.f)
	{
		return;
	}
	// chest-mounted camera: slow wobble, a step rhythm while walking, a jolt on every hit
	Time += DeltaTime;
	BobPhase += DeltaTime * 9.f * WalkSpeed01;
	const float S = WalkSpeed01;
	FRotator Wobble(FMath::PerlinNoise1D(Time * 0.7f) * 0.6f, FMath::PerlinNoise1D(Time * 0.6f + 17.f) * 0.6f,
		FMath::PerlinNoise1D(Time * 0.5f + 41.f) * 0.8f + FMath::Sin(BobPhase) * 0.9f * S);
	Wobble *= Handheld;
	if (JoltLeft > 0.f)
	{
		Wobble += FRotator(FMath::FRandRange(-1.f, 1.f), FMath::FRandRange(-1.f, 1.f), FMath::FRandRange(-1.5f, 1.5f)) * JoltLeft * 4.f;
		JoltLeft = FMath::Max(0.f, JoltLeft - DeltaTime * 2.f);
	}
	const FVector Bob(0.f, FMath::Sin(BobPhase) * 1.4f * S, (FMath::Abs(FMath::Sin(BobPhase)) * 2.4f - 1.2f) * S);
	OutVT.POV.Location += OutVT.POV.Rotation.RotateVector(Bob);
	OutVT.POV.Rotation += Wobble;
}
