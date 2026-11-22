// Copyright Epic Games, Inc. All Rights Reserved.


#include "KadyktschanPlayerController.h"
#include "EnhancedInputSubsystems.h"
#include "Engine/LocalPlayer.h"
#include "InputMappingContext.h"
#include "KadyktschanCameraManager.h"
#include "Blueprint/UserWidget.h"
#include "Kadyktschan.h"
#include "Widgets/Input/SVirtualJoystick.h"
#include "Widgets/Input/SButton.h"
#include "Engine/GameViewportClient.h"
#include "Framework/Application/SlateApplication.h"
#include "KdkGameUserSettings.h"
#include "SKdkSettingsMenu.h"
#include "SKdkTownMap.h"
#include "TimerManager.h"
#include "Widgets/SWeakWidget.h"
#include "Engine/PostProcessVolume.h"
#include "HAL/IConsoleManager.h"
#include "Styling/CoreStyle.h"
#include "Widgets/Layout/SBox.h"
#include "Widgets/SBoxPanel.h"
#include "Widgets/Text/STextBlock.h"
#include "Misc/FileHelper.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "ImageUtils.h"
#include "Engine/Texture2D.h"
#include "SKdkMainMenu.h"
#include "KdkLoc.h"
#include "Misc/Paths.h"
#include "Engine/World.h"
#include "CollisionQueryParams.h"
#include "KdkShooterDirector.h"
#include "KadyktschanCharacter.h"
#include "Misc/DateTime.h"

AKadyktschanPlayerController::AKadyktschanPlayerController()
{
	// set the player camera manager class
	PlayerCameraManagerClass = AKadyktschanCameraManager::StaticClass();
}

void AKadyktschanPlayerController::BeginPlay()
{
	Super::BeginPlay();

	if (IsLocalPlayerController())
	{
		// when the window opens, macOS warps the cursor and the first frames feed one huge look delta that tilts the
		// view to the ground; ignore look input until the window has settled, then level the view
		SetIgnoreLookInput(true);
		GetWorldTimerManager().SetTimer(StartViewTimer, this, &AKadyktschanPlayerController::LevelStartView, 1.5f, false);
		GetWorldTimerManager().SetTimer(CamTimer, this, &AKadyktschanPlayerController::UpdateCamcorder, 0.5f, true);

		// engine debug warnings (shadow map queue, ray tracing memory) are for developers and cover the menu
		ConsoleCommand(TEXT("DisableAllScreenMessages"));

		const UKdkGameUserSettings* Settings = UKdkGameUserSettings::Get();
		if (Settings && Settings->bShowFPS)
		{
			ConsoleCommand(TEXT("stat fps"));
		}

		FString Json;
		if (FFileHelper::LoadFileToString(Json, *(FPaths::ProjectContentDir() / TEXT("Kadykchan/Data/Story.json"))) && Story.Load(Json))
		{
			UGameViewportClient* Viewport = GetWorld()->GetGameViewport();
			TWeakObjectPtr<AKadyktschanPlayerController> Self(this);
			StoryHud = SNew(SKdkStoryHud).State([Self]() -> const FKdkHudState&
			{
				static const FKdkHudState Empty;
				return Self.IsValid() ? Self->Hud : Empty;
			});
			if (Viewport)
			{
				Viewport->AddViewportWidgetContent(StoryHud.ToSharedRef(), 40);
			}
		}
		else
		{
			UE_LOG(LogKadyktschan, Warning, TEXT("Story.json missing or malformed: no objectives"));
		}
		// -KdkEnglish: English for this run only (evidence shots; saved only if the settings menu is closed)
		// (a "-Lang=" switch hung the engine at start-up, 2026-11-09)
		const TCHAR* Cmd = FCommandLine::Get();
		if (FParse::Param(Cmd, TEXT("KdkEnglish")))
		{
			if (UKdkGameUserSettings* S = UKdkGameUserSettings::Get())
			{
				S->Language = TEXT("en");
			}
		}
		// the dev hooks drive the game directly: no menu in their way
		bool bDevRun = false;
		for (const TCHAR* Hook : {TEXT("KdkStart="), TEXT("KdkShot="), TEXT("KdkWalk="), TEXT("KdkStory="), TEXT("KdkNoMenu"), TEXT("KdkShooter")})
		{
			bDevRun |= FString(Cmd).Contains(Hook);
		}
		if (!bDevRun)
		{
			ShowMainMenu();
		}
	}


	// only spawn touch controls on local player controllers
	if (IsLocalPlayerController() && ShouldUseTouchControls())
	{
		// spawn the mobile controls widget
		MobileControlsWidget = CreateWidget<UUserWidget>(this, MobileControlsWidgetClass);

		if (MobileControlsWidget)
		{
			// add the controls to the player screen
			MobileControlsWidget->AddToPlayerScreen(0);

		} else {

			UE_LOG(LogKadyktschan, Error, TEXT("Could not spawn mobile controls widget."));

		}

	}
}

void AKadyktschanPlayerController::SetupInputComponent()
{
	Super::SetupInputComponent();

	// only add IMCs for local player controllers
	if (IsLocalPlayerController())
	{
		InputComponent->BindKey(EKeys::Escape, IE_Pressed, this, &AKadyktschanPlayerController::ToggleSettingsMenu);
		InputComponent->BindKey(EKeys::M, IE_Pressed, this, &AKadyktschanPlayerController::ToggleSettingsMenu);
		InputComponent->BindKey(EKeys::K, IE_Pressed, this, &AKadyktschanPlayerController::ToggleTownMap);
		InputComponent->BindKey(EKeys::Tab, IE_Pressed, this, &AKadyktschanPlayerController::ToggleTownMap);
		InputComponent->BindKey(EKeys::E, IE_Pressed, this, &AKadyktschanPlayerController::StoryInteract);
		InputComponent->BindKey(EKeys::N, IE_Pressed, this, &AKadyktschanPlayerController::ToggleNotebook);
		// shooter mode (ignored in the story)
		InputComponent->BindKey(EKeys::LeftMouseButton, IE_Pressed, this, &AKadyktschanPlayerController::FireOn);
		InputComponent->BindKey(EKeys::LeftMouseButton, IE_Released, this, &AKadyktschanPlayerController::FireOff);
		InputComponent->BindKey(EKeys::RightMouseButton, IE_Pressed, this, &AKadyktschanPlayerController::AimOn);
		InputComponent->BindKey(EKeys::RightMouseButton, IE_Released, this, &AKadyktschanPlayerController::AimOff);
		InputComponent->BindKey(EKeys::R, IE_Pressed, this, &AKadyktschanPlayerController::ReloadKey);

		// Add Input Mapping Context
		if (UEnhancedInputLocalPlayerSubsystem* Subsystem = ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(GetLocalPlayer()))
		{
			for (UInputMappingContext* CurrentContext : DefaultMappingContexts)
			{
				Subsystem->AddMappingContext(CurrentContext, 0);
			}

			// only add these IMCs if we're not using mobile touch input
			if (!ShouldUseTouchControls())
			{
				for (UInputMappingContext* CurrentContext : MobileExcludedMappingContexts)
				{
					Subsystem->AddMappingContext(CurrentContext, 0);
				}
			}
		}
	}
	
}

bool AKadyktschanPlayerController::ShouldUseTouchControls() const
{
	// are we on a mobile platform? Should we force touch?
	return SVirtualJoystick::ShouldDisplayTouchInterface() || bForceTouchControls;
}

void AKadyktschanPlayerController::LevelStartView()
{
	ResetIgnoreLookInput();
	SetControlRotation(FRotator(0.f, GetControlRotation().Yaw, 0.f));
}

void AKadyktschanPlayerController::ToggleSettingsMenu()
{
	if (FurnishingMap.IsValid()) { ToggleFurnishingMap(); return; }
	UGameViewportClient* Viewport = GetWorld() ? GetWorld()->GetGameViewport() : nullptr;
	if (!Viewport)
	{
		return;
	}
	if (SettingsMenu.IsValid())
	{
		Viewport->RemoveViewportWidgetContent(SettingsMenuViewportEntry.ToSharedRef());
		SettingsMenu.Reset();
		SettingsMenuViewportEntry.Reset();
		if (UKdkGameUserSettings* Settings = UKdkGameUserSettings::Get())
		{
			Settings->SaveSettings();
		}
		if (MainMenu.IsValid())  // opened from the main menu: back to it, in the language chosen meanwhile
		{
			ShowMainMenu();
			return;
		}
		SetInputMode(FInputModeGameOnly());
		SetShowMouseCursor(false);
		SetPause(false);
		return;
	}
	if (TownMap.IsValid())
	{
		ToggleTownMap();
	}
	SettingsMenu = SNew(SKdkSettingsMenu).OnClose(FSimpleDelegate::CreateUObject(this, &AKadyktschanPlayerController::ToggleSettingsMenu))
		.OnLanguage(FSimpleDelegate::CreateLambda([this]() { ToggleSettingsMenu(); ToggleSettingsMenu(); }))
		.OnFurnishingMap(FSimpleDelegate::CreateUObject(this, &AKadyktschanPlayerController::ToggleFurnishingMap));  // rebuilt in the new language
	SettingsMenuViewportEntry = SNew(SWeakWidget).PossiblyNullContent(SettingsMenu);
	Viewport->AddViewportWidgetContent(SettingsMenuViewportEntry.ToSharedRef(), 100);
	FInputModeUIOnly Mode;
	Mode.SetWidgetToFocus(SettingsMenu);
	SetInputMode(Mode);
	SetShowMouseCursor(true);
	SetPause(true);
}

void AKadyktschanPlayerController::ToggleTownMap()
{
	UGameViewportClient* Viewport = GetWorld() ? GetWorld()->GetGameViewport() : nullptr;
	if (!Viewport || SettingsMenu.IsValid())
	{
		return;
	}
	if (TownMap.IsValid())
	{
		Viewport->RemoveViewportWidgetContent(TownMap.ToSharedRef());
		TownMap.Reset();
		return;
	}
	TWeakObjectPtr<AKadyktschanPlayerController> Self(this);
	// hit-test invisible: the mouse keeps steering the view while the map is open
	TownMap = SNew(SBox).Padding(FMargin(60.f, 40.f)).Visibility(EVisibility::HitTestInvisible)
		[
			SNew(SKdkTownMap).PlayerView([Self]() -> FVector3f
			{
				const APawn* Pawn = Self.IsValid() ? Self->GetPawn() : nullptr;
				if (!Pawn)
				{
					return FVector3f::ZeroVector;
				}
				// UE X = north, Y = east (centimetres); the map wants east/north metres and yaw from north
				const FVector L = Pawn->GetActorLocation();
				return FVector3f(L.Y / 100.f, L.X / 100.f, Self->GetControlRotation().Yaw);
			})
		];
	Viewport->AddViewportWidgetContent(TownMap.ToSharedRef(), 50);
}

void AKadyktschanPlayerController::ToggleFurnishingMap()
{
	UGameViewportClient* Viewport = GetWorld() ? GetWorld()->GetGameViewport() : nullptr;
	if (!Viewport || !SettingsMenu.IsValid()) return;
	FInputModeUIOnly Mode;
	if (FurnishingMap.IsValid())
	{
		Viewport->RemoveViewportWidgetContent(FurnishingMap.ToSharedRef());
		FurnishingMap.Reset();
		SettingsMenu->SetVisibility(EVisibility::Visible);
		Mode.SetWidgetToFocus(SettingsMenu);
	}
	else
	{
		TWeakObjectPtr<AKadyktschanPlayerController> Self(this);
		TSharedRef<SKdkTownMap> Map = SNew(SKdkTownMap).Detailed(true)
			.OnClose(FSimpleDelegate::CreateUObject(this,&AKadyktschanPlayerController::ToggleFurnishingMap))
			.PlayerView([Self]() -> FVector3f
			{
				const APawn* Pawn = Self.IsValid() ? Self->GetPawn() : nullptr;
				if (!Pawn) return FVector3f::ZeroVector;
				const FVector P=Pawn->GetActorLocation();
				return FVector3f(P.Y/100.f,P.X/100.f,Self->GetControlRotation().Yaw);
			});
		FurnishingMap = SNew(SBox).Padding(FMargin(40,30))
		[
			SNew(SVerticalBox)
			+ SVerticalBox::Slot().FillHeight(1.f)[Map]
			+ SVerticalBox::Slot().AutoHeight().Padding(0,8)
			[
				SNew(SButton).OnClicked_Lambda([Self]() { if (Self.IsValid()) Self->ToggleFurnishingMap(); return FReply::Handled(); })
				[SNew(STextBlock).Text(KdkLoc::T(TEXT("Zurück zu den Einstellungen (Esc)"),TEXT("Back to settings (Esc)")))]
			]
		];
		SettingsMenu->SetVisibility(EVisibility::Collapsed);
		Viewport->AddViewportWidgetContent(FurnishingMap.ToSharedRef(),120);
		Mode.SetWidgetToFocus(Map);
	}
	SetInputMode(Mode);
	SetShowMouseCursor(true);
}

void AKadyktschanPlayerController::UpdateCamcorder()
{
	const UKdkGameUserSettings* Settings = UKdkGameUserSettings::Get();
	// the shooter mode always films; lost health breaks the picture down from the player's own slider values
	// towards a blocky, blurred, noisy wreck (design/gdd/shooter-mode.md, "Leben = Bildqualität")
	const bool bOn = Settings && (Settings->bCamcorder || Shooter.IsValid());
	const float Damage = Shooter.IsValid() ? Shooter->Distortion() : 0.f;
	static float LastPixel = -1.f;
	// the round starts with a clean picture (user 2026-11-11): only hits break it, the story keeps the sliders' look
	const float Pixel = bOn ? FMath::Lerp(Shooter.IsValid() ? 0.f : Settings->CamPixelation, 0.9f, Damage) : 0.f;
	static float LastScale = -1.f;
	if (Pixel != LastPixel || DynScale != LastScale)
	{
		LastScale = DynScale;
		IConsoleVariable* SP = IConsoleManager::Get().FindConsoleVariable(TEXT("r.ScreenPercentage"));
		IConsoleVariable* UQ = IConsoleManager::Get().FindConsoleVariable(TEXT("r.Upscale.Quality"));
		IConsoleVariable* AA = IConsoleManager::Get().FindConsoleVariable(TEXT("r.AntiAliasingMethod"));
		static int32 SavedAA = -1;
		if (AA && SavedAA < 0) { SavedAA = AA->GetInt(); }
		// TSR upscales temporally and smooths the low resolution away; without it the spatial nearest upscale shows blocks
		if (AA) { AA->Set(Pixel > 0.f ? 0 : SavedAA, ECVF_SetByCode); }
		if (Pixel > 0.f && SP && UQ)
		{
			SP->Set(FMath::Lerp(100.f, 20.f, Pixel) * (1.f - 0.6f * Damage) * DynScale, ECVF_SetByCode);  // hits: down to ~10 %
			UQ->Set(0, ECVF_SetByCode);
		}
		else if (Settings && SP)
		{
			if (UQ) { UQ->Set(3, ECVF_SetByCode); }
			// restore with the same (code) priority: a game-setting write cannot override a code-set value
			float N, Scale, Min, Max;
			Settings->GetResolutionScaleInformationEx(N, Scale, Min, Max);
			SP->Set((Scale > 0.f ? Scale : 100.f) * DynScale, ECVF_SetByCode);
		}
		LastPixel = Pixel;
	}
	if (bOn && CamVolume.IsValid())  // noise slider, live
	{
		// one slider scales the whole camcorder look: 0 = no effect, 0.75 = the tuned default, 1 = strongest
		const float K = FMath::Lerp(Shooter.IsValid() ? 0.f : FMath::Clamp(Settings->CamNoise, 0.f, 1.f), 1.f, Damage) / 0.75f;
		FPostProcessSettings& P = CamVolume->Settings;
		if (!Shooter.IsValid())  // the shooter mode sets the blur every frame (PlayerTick)
		{
			P.bOverride_DepthOfFieldFocalDistance = P.bOverride_DepthOfFieldFstop = P.bOverride_DepthOfFieldSensorWidth = false;
		}
		const float Sat = FMath::Max(0.f, 1.f - 0.4f * K);
		P.ColorSaturation = FVector4(Sat, Sat, Sat, 1.0);
		P.ColorGain = FVector4(1.0, 1.0 - 0.02 * K, 1.0 - 0.08 * K, 1.0);
		const float Con = FMath::Max(0.5f, 1.f - 0.15f * K);
		P.ColorContrast = FVector4(Con, Con, Con, 1.0);
		P.FilmGrainIntensity = FMath::Min(1.f, 0.75f * K);
		P.SceneFringeIntensity = 3.5f * K;
		P.VignetteIntensity = FMath::Min(1.f, 0.85f * K);
		P.BloomIntensity = 0.675f + 0.925f * K;
	}
	if (Pixel <= 0.f && Settings)  // keep the resolution slider in charge once the camcorder has used code priority
	{
		float N, Scale, Min, Max;
		Settings->GetResolutionScaleInformationEx(N, Scale, Min, Max);
		IConsoleVariable* SP = IConsoleManager::Get().FindConsoleVariable(TEXT("r.ScreenPercentage"));
		if (SP && Scale > 0.f && !FMath::IsNearlyEqual(SP->GetFloat(), Scale * DynScale))
		{
			SP->Set(Scale * DynScale, ECVF_SetByCode);
		}
	}
	UGameViewportClient* Viewport = GetWorld() ? GetWorld()->GetGameViewport() : nullptr;
	if (bOn && !CamVolume.IsValid())
	{
		// found-footage camcorder: teal, washed out, grainy, soft, colour fringes (user video 2026-11-07)
		APostProcessVolume* V = GetWorld()->SpawnActor<APostProcessVolume>();
		V->bUnbound = true;
		V->Priority = 100.f;
		FPostProcessSettings& P = V->Settings;
		P.bOverride_ColorSaturation = true; P.ColorSaturation = FVector4(0.6, 0.6, 0.6, 1.0);
		P.bOverride_ColorGain = true; P.ColorGain = FVector4(1.0, 0.98, 0.92, 1.0);  // faded warm-neutral, not blue (user 2026-11-07)
		P.bOverride_ColorContrast = true; P.ColorContrast = FVector4(0.85, 0.85, 0.85, 1.0);
		P.bOverride_FilmGrainIntensity = true; P.FilmGrainIntensity = 0.75f;
		P.bOverride_SceneFringeIntensity = true; P.SceneFringeIntensity = 3.5f;
		P.bOverride_VignetteIntensity = true; P.VignetteIntensity = 0.85f;
		P.bOverride_BloomIntensity = true; P.BloomIntensity = 1.6f;
		P.bOverride_DepthOfFieldFstop = false;
		CamVolume = V;
		if (Viewport)
		{
			auto Label = [](const TCHAR* Text, FLinearColor Color)
			{
				return SNew(STextBlock).Text(FText::FromString(Text)).ColorAndOpacity(Color)
					.Font(FCoreStyle::GetDefaultFontStyle("Mono", 28)).ShadowOffset(FVector2D(2, 2));
			};
			CamOverlay = SNew(SBox).Padding(FMargin(60.f, 40.f)).HAlign(HAlign_Right).VAlign(VAlign_Bottom)
				[
					SNew(SVerticalBox)
					+ SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Right)[Label(TEXT("\u25CF REC"), FLinearColor(0.85f, 0.1f, 0.08f, 0.9f))]
					+ SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Right)[Label(TEXT("CAMERA 01"), FLinearColor(0.85f, 0.9f, 0.9f, 0.75f))]
				];
			Viewport->AddViewportWidgetContent(CamOverlay.ToSharedRef(), 10);
		}
	}
	else if (!bOn && CamVolume.IsValid())
	{
		CamVolume->Destroy();
		CamVolume.Reset();
		if (Viewport && CamOverlay.IsValid())
		{
			Viewport->RemoveViewportWidgetContent(CamOverlay.ToSharedRef());
		}
		CamOverlay.Reset();
	}
}

namespace
{
	/** Camera-space direction of a point mapped onto the screen border (0..1), for the marker of an off-screen goal. */
	FVector2f EdgeOf(const FVector& CameraSpace)
	{
		FVector2f V(CameraSpace.Y, -CameraSpace.Z);
		if (CameraSpace.X <= 0.f && V.SizeSquared() < 1.f)
		{
			V = FVector2f(0.f, 1.f);  // straight behind: point down, "turn around"
		}
		V.Normalize();
		const float K = 1.f / FMath::Max(FMath::Abs(V.X) / 0.45f, FMath::Abs(V.Y) / 0.42f);
		return FVector2f(0.5f, 0.5f) + V * K;
	}
}

void AKadyktschanPlayerController::PlayerTick(float DeltaTime)
{
	Super::PlayerTick(DeltaTime);
	if (!StoryHud.IsValid())
	{
		return;
	}
	FVector Eye;
	FRotator Rot;
	GetPlayerViewPoint(Eye, Rot);
	int32 VX = 0, VY = 0;
	GetViewportSize(VX, VY);
	auto Project = [&](const FVector& W, FVector2f& Out) -> bool
	{
		FVector2D S;
		if (VX <= 0 || VY <= 0 || Rot.UnrotateVector(W - Eye).X <= 1.f || !ProjectWorldLocationToScreen(W, S, false))
		{
			return false;
		}
		Out = FVector2f(S.X / VX, S.Y / VY);
		return Out.X >= 0.f && Out.X <= 1.f && Out.Y >= 0.f && Out.Y <= 1.f;
	};
	Hud.bFocusRing = true;
	if (Shooter.IsValid())  // the shooter mode draws its own task, prompt and marker into the same overlay
	{
		FKdkShooterHud V;
		Shooter->FillHud(V);
		Hud.bStoryKeys = false;
		UpdatePerformance(DeltaTime);
		Hud.bCrosshair = !Shooter->IsOver();
		// half the spread cone as a share of the view width (horizontal FOV of the camera)
		const float HalfFov = FMath::DegreesToRadians((PlayerCameraManager ? PlayerCameraManager->GetFOVAngle() : 90.f) * 0.5f);
		Hud.CrosshairGap = FMath::Tan(FMath::DegreesToRadians(V.Spread)) / FMath::Tan(HalfFov) * 0.5f;
		Hud.HitMarker = V.HitMarker;
		Hud.bKillMarker = V.bKill;
		Hud.Aura = 1.f - FMath::Clamp(V.Health, 0.f, 1.f);
		Hud.Marks.Reset();
		for (const FVector4f& M : V.Marks)
		{
			FVector2f S;
			if (Project(FVector(M.X, M.Y, M.Z), S)) Hud.Marks.Add(FVector3f(S.X, S.Y, M.W));
		}
		Hud.Threats.Reset();
		for (const FVector4f& T : V.Threats)
		{
			// direction of the shooter in the view, flattened: forward = up on screen, right = right
			const FVector Local = Rot.UnrotateVector(FVector(T.X, T.Y, T.Z) - Eye);
			const FVector2f Dir = FVector2f(Local.Y, -Local.X).GetSafeNormal();
			Hud.Threats.Add(FVector3f(Dir.X, Dir.Y, T.W));
		}
		if (CamVolume.IsValid())
		{
			// blur only once the camera is really damaged (D^2), and the same at every field of view: aiming narrows
			// the view like a longer lens, so the sensor shrinks with it (the old fixed sensor blurred every aimed shot)
			FPostProcessSettings& P = CamVolume->Settings;
			const float D = Shooter->Distortion();
			const float Blur = D * D;
			P.bOverride_DepthOfFieldFocalDistance = P.bOverride_DepthOfFieldFstop = P.bOverride_DepthOfFieldSensorWidth = Blur > 0.01f;
			P.DepthOfFieldFocalDistance = 60.f;
			P.DepthOfFieldFstop = FMath::Lerp(16.f, 1.4f, Blur);
			P.DepthOfFieldSensorWidth = FMath::Lerp(24.576f, 150.f, Blur) * FMath::Tan(HalfFov) / FMath::Tan(FMath::DegreesToRadians(50.f));
		}
		Hud.Header = V.Header;
		Hud.Goal = V.Goal;
		Hud.Prompt = V.Prompt;
		Hud.bFocusRing = V.bFocus && Project(V.Focus, Hud.Focus);
		Hud.Rings.Reset();
		for (const FVector& R : V.Rings)
		{
			FVector2f S;
			if (Project(R, S)) Hud.Rings.Add(S);
		}
		Hud.bMarker = V.bMarker;
		if (V.bMarker)
		{
			Hud.MarkerDistance = FVector::Dist(GetPawn() ? GetPawn()->GetActorLocation() : Eye, V.Target) / 100.f;
			Hud.bMarkerOnScreen = Project(V.Target, Hud.Marker);
			if (!Hud.bMarkerOnScreen)
			{
				Hud.Marker = EdgeOf(Rot.UnrotateVector(V.Target - Eye));
			}
		}
		return;
	}
	FCollisionQueryParams Params(SCENE_QUERY_STAT(KdkStoryView), true, GetPawn());
	auto Visible = [&](const FVector& P) -> bool
	{
		FHitResult Hit;
		// the find lies on a table or a wall: a hit within a hand's breadth of it still counts as seeing it
		return !GetWorld()->LineTraceSingleByChannel(Hit, Eye, P, ECC_Visibility, Params) || Hit.Distance >= FVector::Dist(Eye, P) - 25.f;
	};

	// the find in focus: any objective's (finds read early count later), within reach and near the view centre
	TArray<FVector> Points;
	TArray<FIntPoint> Index;
	for (int32 S = 0; S < Story.Steps.Num(); ++S)
	{
		for (int32 C = 0; C < Story.Steps[S].Clues.Num(); ++C)
		{
			if (!Story.CanFind(S, C)) continue;
			Points.Add(Story.Steps[S].Clues[C].Pos);
			Index.Add(FIntPoint(S, C));
		}
	}
	const int32 Pick = FKdkStory::Pick(Points, Eye, Rot.Vector(), 230.f, 14.f);
	FocusStep = FocusClue = INDEX_NONE;
	Hud.Prompt.Reset();
	if (Pick != INDEX_NONE && Visible(Points[Pick]) && Project(Points[Pick], Hud.Focus))
	{
		FocusStep = Index[Pick].X;
		FocusClue = Index[Pick].Y;
		const FKdkClue& C = Story.Steps[FocusStep].Clues[FocusClue];
		Hud.Prompt = FString::Printf(TEXT("[E]  %s:  %s"), *KdkLoc::S(C.bFound ? TEXT("Nochmal lesen") : TEXT("Ansehen"),
			C.bFound ? TEXT("Read again") : TEXT("Inspect")), *KdkLoc::S(C.Title, C.TitleEn));
	}

	// objective and marker: the nearest unread find of the open objective, or its entrance while still far away
	Hud.Rings.Reset();
	Hud.bMarker = false;
	const FKdkStoryStep* Step = Story.CurrentStep();
	if (!Step)
	{
		Hud.Header = KdkLoc::S(TEXT("GESCHICHTE ABGESCHLOSSEN"), TEXT("STORY COMPLETE"));
		Hud.Goal = KdkLoc::S(TEXT("Du hast alle Spuren gefunden. Alles Gefundene steht im Notizbuch (N)."),
			TEXT("You have found every trace. Everything you found is in the notebook (N)."));
		return;
	}
	Hud.Header = FString::Printf(TEXT("%s %d / %d   ·   %s"), *KdkLoc::S(TEXT("AUFGABE"), TEXT("TASK")), Story.Current + 1,
		Story.Steps.Num(), *KdkLoc::S(Step->Place, Step->PlaceEn));
	Hud.Goal = KdkLoc::S(Step->Goal, Step->GoalEn);
	const FVector Me = GetPawn() ? GetPawn()->GetActorLocation() : Eye;
	const FKdkClue* Next = nullptr;
	for (int32 CIndex = 0; CIndex < Step->Clues.Num(); ++CIndex)
	{
		if (!Story.CanFind(Story.Current, CIndex)) continue;
		const FKdkClue& C = Step->Clues[CIndex];
		if (!C.bFound && (!Next || FVector::DistSquared(Me, C.Pos) < FVector::DistSquared(Me, Next->Pos)))
		{
			Next = &C;
		}
		FVector2f R;
		if (!C.bFound && FVector::Dist(Eye, C.Pos) < 1000.f && Visible(C.Pos) && Project(C.Pos, R))
		{
			Hud.Rings.Add(R);
		}
	}
	// "inside": clearly nearer to the find than the entrance is (the finds lie deeper in the house than its door)
	const bool bInside = Next && FVector::Dist2D(Me, Next->Pos) < FVector::Dist2D(Step->Door, Next->Pos) - 150.f;
	const FVector Target = bInside ? Next->Pos : Step->Door;
	Hud.bMarker = true;
	Hud.MarkerDistance = FVector::Dist(Me, Target) / 100.f;
	Hud.bMarkerOnScreen = Project(Target, Hud.Marker);
	if (!Hud.bMarkerOnScreen)
	{
		Hud.Marker = EdgeOf(Rot.UnrotateVector(Target - Eye));
	}
}

void AKadyktschanPlayerController::StoryInteract()
{
	if (Shooter.IsValid())
	{
		if (Shooter->IsOver() && !Hud.ReaderTitle.IsEmpty())
		{
			EndShooter();
		}
		else if (!SettingsMenu.IsValid())
		{
			Shooter->Interact();
		}
		return;
	}
	if (!Hud.ReaderTitle.IsEmpty())  // close the text; an objective that just closed tells what it means next
	{
		Hud.ReaderTitle.Reset();
		Hud.ReaderText.Reset();
		if (PendingTexts.Num() > 0)
		{
			Hud.ReaderTitle = PendingTexts[0].Key;
			Hud.ReaderText = PendingTexts[0].Value;
			PendingTexts.RemoveAt(0);
		}
		return;
	}
	if (FocusStep == INDEX_NONE || SettingsMenu.IsValid())
	{
		return;
	}
	Hud.Notebook.Reset();
	const FKdkClue& C = Story.Steps[FocusStep].Clues[FocusClue];
	Hud.ReaderTitle = KdkLoc::S(C.Title, C.TitleEn);
	Hud.ReaderText = KdkLoc::S(C.Text, C.TextEn);
	for (const int32 Done : Story.Find(FocusStep, FocusClue))
	{
		FString Text = KdkLoc::S(Story.Steps[Done].Done, Story.Steps[Done].DoneEn);
		if (Story.Steps.IsValidIndex(Done + 1))
		{
			Text += KdkLoc::S(TEXT("\n\nNächste Aufgabe: "), TEXT("\n\nNext task: ")) + KdkLoc::S(Story.Steps[Done + 1].Goal, Story.Steps[Done + 1].GoalEn);
		}
		PendingTexts.Add(TPair<FString, FString>(KdkLoc::S(TEXT("Neue Erkenntnis"), TEXT("New insight")), Text));
	}
}

void AKadyktschanPlayerController::ToggleNotebook()
{
	if (!StoryHud.IsValid() || SettingsMenu.IsValid() || Shooter.IsValid())
	{
		return;
	}
	if (!Hud.Notebook.IsEmpty())
	{
		Hud.Notebook.Reset();
		return;
	}
	Hud.ReaderTitle.Reset();
	FString Book;
	for (int32 S = 0; S <= FMath::Min(Story.Current, Story.Steps.Num() - 1); ++S)
	{
		const FKdkStoryStep& Step = Story.Steps[S];
		const bool bDone = S < Story.Current;
		Book += FString::Printf(TEXT("%s  %s\n"), bDone ? TEXT("[x]") : TEXT("[  ]"), *KdkLoc::S(Step.Place, Step.PlaceEn));
		if (bDone)
		{
			Book += TEXT("      ") + KdkLoc::S(Step.Done, Step.DoneEn).Replace(TEXT("\n\n"), TEXT(" ")) + TEXT("\n\n");
			continue;
		}
		for (const FKdkClue& C : Step.Clues)
		{
			Book += FString::Printf(TEXT("      %s %s\n"), C.bFound ? TEXT("–") : TEXT("?"),
				C.bFound ? *KdkLoc::S(C.Title, C.TitleEn) : *KdkLoc::S(TEXT("(noch nicht gefunden)"), TEXT("(not found yet)")));
		}
	}
	Hud.Notebook = Book.TrimEnd();
}

void AKadyktschanPlayerController::ShowMainMenu()
{
	UGameViewportClient* Viewport = GetWorld() ? GetWorld()->GetGameViewport() : nullptr;
	if (!Viewport)
	{
		return;
	}
	if (!TitleTexture)
	{
		TitleTexture = FImageUtils::ImportFileAsTexture2D(FPaths::ProjectContentDir() / TEXT("Kadykchan/Data/UI/Title.png"));
		if (TitleTexture)
		{
			TitleBrush.SetResourceObject(TitleTexture);
			TitleBrush.ImageSize = FVector2D(TitleTexture->GetSizeX(), TitleTexture->GetSizeY());
		}
	}
	if (MainMenu.IsValid())
	{
		Viewport->RemoveViewportWidgetContent(MainMenu.ToSharedRef());
	}
	TSharedRef<SKdkMainMenu> Menu = SNew(SKdkMainMenu)
		.Picture(TitleTexture ? &TitleBrush : nullptr)
		.OnStart(FSimpleDelegate::CreateUObject(this, &AKadyktschanPlayerController::CloseMainMenu))
		.OnShooter(FSimpleDelegate::CreateLambda([this]() { CloseMainMenu(); StartShooter(); }))
		.OnSettings(FSimpleDelegate::CreateUObject(this, &AKadyktschanPlayerController::ToggleSettingsMenu))
		.OnLanguage(FSimpleDelegate::CreateLambda([this]()
		{
			if (UKdkGameUserSettings* S = UKdkGameUserSettings::Get())
			{
				S->Language = KdkLoc::IsEnglish() ? TEXT("de") : TEXT("en");
				S->SaveSettings();
			}
			ShowMainMenu();
		}))
		.OnQuit(FSimpleDelegate::CreateLambda([this]() { ConsoleCommand(TEXT("quit")); }));
	MainMenu = Menu;
	const UKdkGameUserSettings* Settings = UKdkGameUserSettings::Get();
	if (Settings && Settings->bShowFPS && !bFpsHiddenForMenu)
	{
		ConsoleCommand(TEXT("stat fps"));
		bFpsHiddenForMenu = true;
	}
	Viewport->AddViewportWidgetContent(Menu, 90);  // under the settings menu (100), over the story overlay (40)
	FInputModeUIOnly Mode;
	Mode.SetWidgetToFocus(Menu);
	SetInputMode(Mode);
	SetShowMouseCursor(true);
	SetPause(true);
}

void AKadyktschanPlayerController::CloseMainMenu()
{
	UGameViewportClient* Viewport = GetWorld() ? GetWorld()->GetGameViewport() : nullptr;
	if (Viewport && MainMenu.IsValid())
	{
		Viewport->RemoveViewportWidgetContent(MainMenu.ToSharedRef());
	}
	MainMenu.Reset();
	if (bFpsHiddenForMenu)
	{
		ConsoleCommand(TEXT("stat fps"));
		bFpsHiddenForMenu = false;
	}
	SetInputMode(FInputModeGameOnly());
	SetShowMouseCursor(false);
	SetPause(false);
}

bool AKadyktschanPlayerController::IsTownPowerOn() const
{
	if (Shooter.IsValid())
	{
		return Shooter->IsPowerOn();
	}
	return !Story.Steps.IsEmpty() && Story.Steps[0].Id == TEXT("power") && Story.IsStepComplete(0);
}

void AKadyktschanPlayerController::StartShooter(int32 Seed)
{
	if (Shooter.IsValid() || !GetPawn())
	{
		return;
	}
	AKdkShooterDirector* Director = GetWorld()->SpawnActor<AKdkShooterDirector>();
	const int32 RoundSeed = Seed >= 0 ? Seed : int32(FDateTime::Now().GetTicks() % 1000000);
	if (!Director || !Director->BeginRound(this, RoundSeed))
	{
		if (Director) Director->Destroy();
		Hud.ReaderTitle = KdkLoc::S(TEXT("Einsatz nicht verfügbar"), TEXT("Mission not available"));
		Hud.ReaderText = KdkLoc::S(TEXT("Die Einsatzdaten fehlen (tools/rebuild_shooter.sh)."), TEXT("The mission data is missing (tools/rebuild_shooter.sh)."));
		return;
	}
	Shooter = Director;
	Hud.Notebook.Reset();
	Hud.ReaderTitle.Reset();
	PendingTexts.Reset();
	UpdateCamcorder();
	UpdateCamcorder();  // the first call spawns the camcorder volume, the second sets it to the undamaged look
}

void AKadyktschanPlayerController::EndShooter()
{
	if (!Shooter.IsValid())
	{
		return;
	}
	Shooter->Destroy();  // EndRound: removes the round and puts the player back where the story left them
	Shooter.Reset();
	SetPerfLevel(0);  // the player's own graphics settings again
	Hud = FKdkHudState();
	ResetIgnoreMoveInput();
	UpdateCamcorder();
	ShowMainMenu();
}

void AKadyktschanPlayerController::OnShooterHurt()
{
	UpdateCamcorder();
	if (AKadyktschanCameraManager* Cam = Cast<AKadyktschanCameraManager>(PlayerCameraManager))
	{
		Cam->Jolt(0.6f);
	}
}

void AKadyktschanPlayerController::ShowShooterResult(const FString& Title, const FString& Text)
{
	Hud.ReaderTitle = Title;
	Hud.ReaderText = Text;
	SetIgnoreMoveInput(true);
}

void AKadyktschanPlayerController::FireOn()
{
	if (Shooter.IsValid() && !SettingsMenu.IsValid()) Shooter->SetFiring(true);
}

void AKadyktschanPlayerController::FireOff()
{
	if (Shooter.IsValid()) Shooter->SetFiring(false);
}

void AKadyktschanPlayerController::AimOn()
{
	if (Shooter.IsValid() && !SettingsMenu.IsValid()) Shooter->SetAiming(true);
}

void AKadyktschanPlayerController::AimOff()
{
	if (Shooter.IsValid()) Shooter->SetAiming(false);
}

void AKadyktschanPlayerController::ReloadKey()
{
	if (Shooter.IsValid()) Shooter->Reload();
}

void AKadyktschanPlayerController::UpdatePerformance(float DeltaTime)
{
	// frame rate per second; below the target for 2 s: one level down, well above it for 6 s: one level up again
	PerfTime += DeltaTime;
	++PerfFrames;
	if (PerfTime < 1.f || !Shooter.IsValid())
	{
		return;
	}
	const float Fps = PerfFrames / PerfTime;
	PerfTime = 0.f;
	PerfFrames = 0;
	const float Target = Shooter->Rules.TargetFps;
	BelowFor = Fps < Target - 3.f ? BelowFor + 1.f : 0.f;
	AboveFor = Fps > Target + 15.f ? AboveFor + 1.f : 0.f;
	if (BelowFor >= 2.f && PerfLevel < 4)
	{
		SetPerfLevel(PerfLevel + 1);
		BelowFor = 0.f;
	}
	else if (AboveFor >= 6.f && PerfLevel > 0)
	{
		SetPerfLevel(PerfLevel - 1);
		AboveFor = 0.f;
	}
}

void AKadyktschanPlayerController::SetPerfLevel(int32 Level)
{
	if (Level == PerfLevel)
	{
		return;
	}
	if (PerfLevel == 0)
	{
		SavedQuality = Scalability::GetQualityLevels();  // the player's settings: never saved over, restored at level 0
	}
	PerfLevel = Level;
	// every level lowers resolution and settings together, each setting one step per level below the player's own
	// (user 2026-11-11: "nicht nur die Auflösung"), down to a floor that keeps the look: lighting never 0 (Lumen
	// off turns the rooms black), shadows never off, view distance never below 1 (the forest silhouette)
	// resolution only late and mildly: a lower resolution reads as blur (user 2026-11-11 "es wird nur alles unscharf")
	static const float Res[] = {1.f, 1.f, 1.f, 0.85f, 0.75f};
	DynScale = Res[Level];
	Scalability::FQualityLevels Q = SavedQuality;
	auto Lower = [Level](int32& Value, int32 FromLevel, int32 Floor)  // from FromLevel on, one step per level
	{
		const int32 Steps = FMath::Max(0, Level - FromLevel + 1);
		Value = Value <= Floor ? Value : FMath::Max(Floor, Value - Steps);
	};
	Lower(Q.ShadowQuality, 1, 1);  // 0 switches shadows off: the town looks flat
	Lower(Q.FoliageQuality, 1, 1);
	Lower(Q.EffectsQuality, 1, 0);
	Lower(Q.ReflectionQuality, 2, 0);
	Lower(Q.PostProcessQuality, 2, 1);
	Lower(Q.GlobalIlluminationQuality, 3, 1);
	Lower(Q.ShadingQuality, 3, 1);
	Lower(Q.ViewDistanceQuality, 4, 1);
	if (UKdkGameUserSettings* Settings = UKdkGameUserSettings::Get())
	{
		// any save meanwhile (settings menu, quitting) writes the player's levels, not these
		if (Level > 0) Settings->TemporaryQualityOverride = SavedQuality;
		else Settings->TemporaryQualityOverride.Reset();
	}
	// bForce: the saved levels were loaded with the game-setting priority, a plain (scalability priority) write is
	// ignored - that is why only the resolution changed at first
	Scalability::SetQualityLevels(Q, true);
	UpdateCamcorder();
	Q = Scalability::GetQualityLevels();  // log what is really active
	UE_LOG(LogKadyktschan, Display, TEXT("Shooter graphics level %d (resolution x%.2f, shadows %d, foliage %d, effects %d, reflections %d, post %d, GI %d, shading %d, view %d)"),
		Level, DynScale, Q.ShadowQuality, Q.FoliageQuality, Q.EffectsQuality, Q.ReflectionQuality, Q.PostProcessQuality, Q.GlobalIlluminationQuality,
		Q.ShadingQuality, Q.ViewDistanceQuality);
	if (Shooter.IsValid())
	{
		Shooter->Toast(FString::Printf(TEXT("Grafik automatisch angepasst: Stufe %d"), Level),
			FString::Printf(TEXT("Graphics adjusted automatically: level %d"), Level));
	}
}
