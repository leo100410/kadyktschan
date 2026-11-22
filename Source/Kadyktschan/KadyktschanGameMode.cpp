// Copyright Epic Games, Inc. All Rights Reserved.

#include "KadyktschanGameMode.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/Pawn.h"
#include "Camera/PlayerCameraManager.h"
#include "Engine/World.h"
#include "HAL/PlatformMisc.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "TimerManager.h"

AKadyktschanGameMode::AKadyktschanGameMode()
{
	// stub
}

void AKadyktschanGameMode::BeginPlay()
{
	Super::BeginPlay();

	if (!FParse::Value(FCommandLine::Get(), TEXT("KdkShot="), EvidenceShotPath))
	{
		return;
	}
	float Delay = 6.f;
	FParse::Value(FCommandLine::Get(), TEXT("KdkShotDelay="), Delay);
	GetWorldTimerManager().SetTimer(EvidenceTimer, this, &AKadyktschanGameMode::TakeEvidenceShot, Delay, false);
}

void AKadyktschanGameMode::TakeEvidenceShot()
{
	APlayerController* PC = GetWorld()->GetFirstPlayerController();
	UE_LOG(LogTemp, Warning, TEXT("KdkShot: capturing to %s (player controller %s)"), *EvidenceShotPath, PC ? TEXT("found") : TEXT("missing"));
	if (!PC)
	{
		FPlatformMisc::RequestExit(false);
		return;
	}
	if (const APawn* Pawn = PC->GetPawn())
	{
		UE_LOG(LogTemp, Warning, TEXT("KdkShot: pawn %s at %s velocity %s control %s camera %s"), *Pawn->GetName(), *Pawn->GetActorLocation().ToString(),
			*Pawn->GetVelocity().ToString(), *PC->GetControlRotation().ToString(),
			PC->PlayerCameraManager ? *PC->PlayerCameraManager->GetCameraRotation().ToString() : TEXT("none"));
	}
	// the OS cursor moves while the window opens and feeds look input; level the view on the start yaw for a reproducible shot
	PC->SetIgnoreLookInput(true);
	FRotator View = PC->GetControlRotation();
	if (const AActor* Start = FindPlayerStart(PC))
	{
		View.Yaw = Start->GetActorRotation().Yaw;
	}
	View.Pitch = 0.f;
	View.Roll = 0.f;
	PC->SetControlRotation(View);
	// HighResShot is handled by the game viewport, which only console commands from a player controller reach;
	// fire it a moment later so the levelled view has rendered
	GetWorldTimerManager().SetTimer(QuitTimer, FTimerDelegate::CreateWeakLambda(this, [this, PC]()
	{
		PC->ConsoleCommand(FString::Printf(TEXT("HighResShot 1280x720 filename=%s"), *EvidenceShotPath));
		// the file is written on a later frame; give it time to reach the disk before quitting
		GetWorldTimerManager().SetTimer(QuitTimer, FTimerDelegate::CreateLambda([]() { FPlatformMisc::RequestExit(false); }), 3.f, false);
	}), 1.f, false);
}
