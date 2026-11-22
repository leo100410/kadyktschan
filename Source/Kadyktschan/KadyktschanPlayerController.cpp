// Copyright Epic Games, Inc. All Rights Reserved.


#include "KadyktschanPlayerController.h"
#include "EnhancedInputSubsystems.h"
#include "Engine/LocalPlayer.h"
#include "InputMappingContext.h"
#include "KadyktschanCameraManager.h"
#include "Blueprint/UserWidget.h"
#include "Kadyktschan.h"
#include "Widgets/Input/SVirtualJoystick.h"
#include "Engine/GameViewportClient.h"
#include "Framework/Application/SlateApplication.h"
#include "KdkGameUserSettings.h"
#include "SKdkSettingsMenu.h"
#include "TimerManager.h"
#include "Widgets/SWeakWidget.h"
#include "Engine/PostProcessVolume.h"
#include "HAL/IConsoleManager.h"
#include "Styling/CoreStyle.h"
#include "Widgets/Layout/SBox.h"
#include "Widgets/SBoxPanel.h"
#include "Widgets/Text/STextBlock.h"

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
		SetInputMode(FInputModeGameOnly());
		SetShowMouseCursor(false);
		SetPause(false);
		return;
	}
	SettingsMenu = SNew(SKdkSettingsMenu).OnClose(FSimpleDelegate::CreateUObject(this, &AKadyktschanPlayerController::ToggleSettingsMenu));
	SettingsMenuViewportEntry = SNew(SWeakWidget).PossiblyNullContent(SettingsMenu);
	Viewport->AddViewportWidgetContent(SettingsMenuViewportEntry.ToSharedRef(), 100);
	FInputModeUIOnly Mode;
	Mode.SetWidgetToFocus(SettingsMenu);
	SetInputMode(Mode);
	SetShowMouseCursor(true);
	SetPause(true);
}

void AKadyktschanPlayerController::UpdateCamcorder()
{
	const UKdkGameUserSettings* Settings = UKdkGameUserSettings::Get();
	const bool bOn = Settings && Settings->bCamcorder;
	// pixelation: drop the render resolution and upscale without filtering (nearest neighbour)
	static float LastPixel = -1.f;
	const float Pixel = bOn ? Settings->CamPixelation : 0.f;
	if (Pixel != LastPixel)
	{
		IConsoleVariable* SP = IConsoleManager::Get().FindConsoleVariable(TEXT("r.ScreenPercentage"));
		IConsoleVariable* UQ = IConsoleManager::Get().FindConsoleVariable(TEXT("r.Upscale.Quality"));
		IConsoleVariable* AA = IConsoleManager::Get().FindConsoleVariable(TEXT("r.AntiAliasingMethod"));
		static int32 SavedAA = -1;
		if (AA && SavedAA < 0) { SavedAA = AA->GetInt(); }
		// TSR upscales temporally and smooths the low resolution away; without it the spatial nearest upscale shows blocks
		if (AA) { AA->Set(Pixel > 0.f ? 0 : SavedAA, ECVF_SetByCode); }
		if (Pixel > 0.f && SP && UQ)
		{
			SP->Set(FMath::Lerp(100.f, 20.f, Pixel), ECVF_SetByCode);
			UQ->Set(0, ECVF_SetByCode);
		}
		else if (Settings && SP)
		{
			if (UQ) { UQ->Set(3, ECVF_SetByCode); }
			// restore with the same (code) priority: a game-setting write cannot override a code-set value
			float N, Scale, Min, Max;
			Settings->GetResolutionScaleInformationEx(N, Scale, Min, Max);
			SP->Set(Scale > 0.f ? Scale : 100.f, ECVF_SetByCode);
		}
		LastPixel = Pixel;
	}
	if (bOn && CamVolume.IsValid())  // noise slider, live
	{
		// one slider scales the whole camcorder look: 0 = no effect, 0.75 = the tuned default, 1 = strongest
		const float K = FMath::Clamp(Settings->CamNoise, 0.f, 1.f) / 0.75f;
		FPostProcessSettings& P = CamVolume->Settings;
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
		if (SP && Scale > 0.f && !FMath::IsNearlyEqual(SP->GetFloat(), Scale))
		{
			SP->Set(Scale, ECVF_SetByCode);
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
