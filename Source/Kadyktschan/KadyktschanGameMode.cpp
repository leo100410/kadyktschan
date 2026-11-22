// Copyright Epic Games, Inc. All Rights Reserved.

#include "KadyktschanGameMode.h"
#include "KdkTownPower.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/Pawn.h"
#include "Camera/PlayerCameraManager.h"
#include "Engine/World.h"
#include "HAL/PlatformMisc.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "UnrealClient.h"
#include "Containers/Ticker.h"
#include "TimerManager.h"
#include "Engine/World.h"
#include "KadyktschanCharacter.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "KadyktschanPlayerController.h"
#include "KdkShooterDirector.h"

AKadyktschanGameMode::AKadyktschanGameMode()
{
	// ticks only to drive the -KdkWalk check (movement input has to be given every frame)
	PrimaryActorTick.bCanEverTick = true;
}

void AKadyktschanGameMode::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	if (bWalking)
	{
		WalkStep(DeltaSeconds);
	}
}

void AKadyktschanGameMode::BeginPlay()
{
	Super::BeginPlay();
	GetWorld()->SpawnActor<AKdkTownPower>();

	// after the controller's own start-view levelling (1.5 s)
	GetWorldTimerManager().SetTimer(StartTimer, this, &AKadyktschanGameMode::ApplyDevStart, 2.f, false);
	if (!FParse::Value(FCommandLine::Get(), TEXT("KdkShot="), EvidenceShotPath))
	{
		return;
	}
	float Delay = 6.f;
	FParse::Value(FCommandLine::Get(), TEXT("KdkShotDelay="), Delay);
	// the core ticker runs while the game is paused too (shots of the main menu, e.g. after -KdkEndShooter)
	FTSTicker::GetCoreTicker().AddTicker(FTickerDelegate::CreateWeakLambda(this, [this](float) { TakeEvidenceShot(); return false; }), Delay);
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
	if (ShotYaw != TNumericLimits<float>::Max())
	{
		View.Yaw = ShotYaw;
	}
	else if (const AActor* Start = FindPlayerStart(PC))
	{
		View.Yaw = Start->GetActorRotation().Yaw;
	}
	View.Pitch = ShotPitch;
	View.Roll = 0.f;
	PC->SetControlRotation(View);
	// HighResShot is handled by the game viewport, which only console commands from a player controller reach;
	// fire it a moment later so the levelled view has rendered
	FTSTicker::GetCoreTicker().AddTicker(FTickerDelegate::CreateWeakLambda(this, [this, PC](float)
	{
		if (FParse::Param(FCommandLine::Get(), TEXT("KdkShotUI")))
		{
			FScreenshotRequest::RequestScreenshot(EvidenceShotPath, true, false);  // with the overlay (task, prompt, panels)
		}
		else
		{
			PC->ConsoleCommand(FString::Printf(TEXT("HighResShot 1280x720 filename=%s"), *EvidenceShotPath));
		}
		// the file is written on a later frame; give it time to reach the disk before quitting
		FTSTicker::GetCoreTicker().AddTicker(FTickerDelegate::CreateLambda([](float) { FPlatformMisc::RequestExit(false); return false; }), 3.f);
		return false;
	}), 1.f);
}

void AKadyktschanGameMode::ApplyDevStart()
{
	APlayerController* PC = GetWorld()->GetFirstPlayerController();
	APawn* Pawn = PC ? PC->GetPawn() : nullptr;
	if (!Pawn)
	{
		return;
	}
	const TCHAR* Cmd = FCommandLine::Get();
	FString Start, Walk;
	// -KdkShooter[=seed]: straight into a shooter round; -KdkHealth=<0..100> shows the camcorder at that damage
	FString ShooterSeed;
	if (FParse::Param(Cmd, TEXT("KdkShooter")) || FParse::Value(Cmd, TEXT("KdkShooter="), ShooterSeed))
	{
		if (AKadyktschanPlayerController* KPC = Cast<AKadyktschanPlayerController>(PC))
		{
			KPC->StartShooter(ShooterSeed.IsEmpty() ? 1 : FCString::Atoi(*ShooterSeed));
			if (FParse::Param(Cmd, TEXT("KdkAim")))  // hold the right mouse button (aim, peek out of cover)
			{
				TWeakObjectPtr<AKadyktschanPlayerController> WeakAim(KPC);
				FTimerHandle AimHandle;
				GetWorldTimerManager().SetTimer(AimHandle, [WeakAim]() { if (WeakAim.IsValid() && WeakAim->GetShooter()) WeakAim->GetShooter()->SetAiming(true); }, 1.5f, false);
			}
			float EndAfter = 0.f;  // -KdkEndShooter=<s>: back to the story world and the main menu (return path check)
			if (FParse::Value(Cmd, TEXT("KdkEndShooter="), EndAfter))
			{
				TWeakObjectPtr<AKadyktschanPlayerController> Weak(KPC);
				FTimerHandle EndHandle;
				GetWorldTimerManager().SetTimer(EndHandle, [Weak]() { if (Weak.IsValid()) Weak->EndShooter(); }, EndAfter, false);
			}
			float Health = 0.f;
			if (KPC->GetShooter() && FParse::Value(Cmd, TEXT("KdkHealth="), Health))
			{
				KPC->GetShooter()->Rules.Health = KPC->GetShooter()->Rules.Vision = Health;
				KPC->GetShooter()->Rules.RegenDelay = 1.0e9f;  // evidence shots: hold the damage, no recovery
				KPC->OnShooterHurt();
			}
		}
	}
	if (FParse::Value(Cmd, TEXT("KdkStart="), Start, false))
	{
		TArray<FString> V;
		Start.ParseIntoArray(V, TEXT(","));
		if (V.Num() >= 3 && V.Num() <= 6)  // north,east,yaw[,pitch[,hover metres[,look down from z metres: inside a house]]]
		{
			const FVector XY(FCString::Atof(*V[0]) * 100.f, FCString::Atof(*V[1]) * 100.f, 0.f);
			FHitResult Hit;  // stand on whatever is below (terrain or a floor)
			const float From = V.Num() == 6 ? FCString::Atof(*V[5]) * 100.f : 50000.f;
			const bool bFloor = GetWorld()->LineTraceSingleByChannel(Hit, FVector(XY.X, XY.Y, From), XY - FVector(0, 0, 50000), ECC_Visibility);
			const float HalfHeight = Pawn->GetSimpleCollisionHalfHeight();
			const float Hover = V.Num() == 5 ? FCString::Atof(*V[4]) * 100.f : 0.f;
			if (ACharacter* Character = Cast<ACharacter>(Pawn); Character && Hover > 0.f)
			{
				Character->GetCharacterMovement()->SetMovementMode(MOVE_Flying);  // overview shots: hold the camera in the air
			}
			Pawn->SetActorLocation(FVector(XY.X, XY.Y, (bFloor ? Hit.ImpactPoint.Z : 0.f) + HalfHeight + 5.f + Hover), false, nullptr, ETeleportType::TeleportPhysics);
			ShotYaw = FCString::Atof(*V[2]);
			ShotPitch = V.Num() >= 4 ? FCString::Atof(*V[3]) : 0.f;
			PC->SetControlRotation(FRotator(ShotPitch, ShotYaw, 0.f));
			if (V.Num() >= 4)
			{
				PC->SetIgnoreLookInput(true);  // the OS cursor moving while the window opens would turn the test view
			}
			UE_LOG(LogTemp, Warning, TEXT("KdkStart: pawn at %s"), *Pawn->GetActorLocation().ToString());
		}
	}
	if (FParse::Param(Cmd, TEXT("KdkCover")))  // shooter: take cover (Q) where -KdkStart put the player
	{
		if (AKadyktschanCharacter* Character = Cast<AKadyktschanCharacter>(Pawn))
		{
			FTimerHandle CoverHandle;
			TWeakObjectPtr<AKadyktschanCharacter> Weak(Character);
			GetWorldTimerManager().SetTimer(CoverHandle, [Weak]() { if (Weak.IsValid()) Weak->QPressed(); }, 0.5f, false);
		}
	}
	if (FParse::Param(Cmd, TEXT("KdkTorch")))
	{
		if (AKadyktschanCharacter* Character = Cast<AKadyktschanCharacter>(Pawn))
		{
			Character->ToggleFlashlight();
		}
	}
	if (AKadyktschanPlayerController* KPC = Cast<AKadyktschanPlayerController>(PC))  // story evidence shots
	{
		int32 Step = 0;
		if (FParse::Value(Cmd, TEXT("KdkStory="), Step))
		{
			KPC->StorySkipTo(Step);
		}
		// the view needs a frame to settle on the find before E or N
		TWeakObjectPtr<AKadyktschanPlayerController> Weak(KPC);
		FTimerHandle Handle;
		if (FParse::Param(Cmd, TEXT("KdkInspect")))  // in a shooter round only once the enemies are placed
		{
			GetWorldTimerManager().SetTimer(Handle, [Weak]() { if (Weak.IsValid()) { Weak->StoryInteract(); } }, KPC->IsShooter() ? 10.f : 1.0f, false);
		}
		if (FParse::Param(Cmd, TEXT("KdkNotebook")))
		{
			GetWorldTimerManager().SetTimer(Handle, [Weak]() { if (Weak.IsValid()) { Weak->ToggleNotebook(); } }, 1.0f, false);
		}
	}
	if (FParse::Param(Cmd, TEXT("KdkMap")))
	{
		if (AKadyktschanPlayerController* KPC = Cast<AKadyktschanPlayerController>(PC))
		{
			KPC->ToggleTownMap();
		}
	}
	if (FParse::Value(Cmd, TEXT("KdkWalk="), Walk, false))
	{
		TArray<FString> Points;
		Walk.ParseIntoArray(Points, TEXT(";"));
		for (const FString& P : Points)
		{
			FString N, E;
			if (P.Split(TEXT(","), &N, &E))
			{
				WalkPoints.Add(FVector2D(FCString::Atof(*N) * 100.f, FCString::Atof(*E) * 100.f));
			}
		}
		WalkLastPos = Pawn->GetActorLocation();
		bWalking = WalkPoints.Num() > 0;
	}
}

void AKadyktschanGameMode::WalkStep(float DeltaSeconds)
{
	APlayerController* PC = GetWorld()->GetFirstPlayerController();
	APawn* Pawn = PC ? PC->GetPawn() : nullptr;
	if (!Pawn || !WalkPoints.IsValidIndex(WalkIndex))
	{
		bWalking = false;
		return;
	}
	const FVector Pos = Pawn->GetActorLocation();
	const FVector2D To = WalkPoints[WalkIndex] - FVector2D(Pos.X, Pos.Y);
	if (To.Size() < 60.f)  // a capsule radius and a bit: rails and sills can hold it a few cm short
	{
		UE_LOG(LogTemp, Warning, TEXT("KdkWalk: reached waypoint %d at %s"), WalkIndex, *Pos.ToString());
		WalkStuckTime = 0.f;
		bWalking = WalkPoints.IsValidIndex(++WalkIndex);
		return;
	}
	ShotYaw = FMath::RadiansToDegrees(FMath::Atan2(To.Y, To.X));
	PC->SetControlRotation(FRotator(0.f, ShotYaw, 0.f));
	Pawn->AddMovementInput(FVector(To.GetSafeNormal(), 0.f), 1.f);
	// stuck = less than 30 cm of progress in 2 s
	WalkStuckTime += DeltaSeconds;
	if (WalkStuckTime > 2.f)
	{
		if (FVector::Dist2D(Pos, WalkLastPos) < 30.f)
		{
			// name what is in the way: sweep the pawn's own capsule half a metre ahead
			FHitResult Hit;
			FCollisionQueryParams Params(TEXT("KdkWalk"), true, Pawn);
			GetWorld()->SweepSingleByChannel(Hit, Pos, Pos + FVector(To.GetSafeNormal(), 0.f) * 50.f, FQuat::Identity, ECC_Pawn,
				FCollisionShape::MakeCapsule(34.f, 96.f), Params);
			UE_LOG(LogTemp, Warning, TEXT("KdkWalk: stuck before waypoint %d at %s, blocked by %s / %s at %s"), WalkIndex, *Pos.ToString(),
				*GetNameSafe(Hit.GetActor()), *GetNameSafe(Hit.GetComponent()), *Hit.ImpactPoint.ToString());
			bWalking = false;
		}
		WalkStuckTime = 0.f;
		WalkLastPos = Pos;
	}
}
