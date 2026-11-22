#include "KdkSkyCycle.h"
#include "Components/DirectionalLightComponent.h"
#include "Engine/DirectionalLight.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "HAL/IConsoleManager.h"
#include "KdkGameUserSettings.h"
#include "EngineUtils.h"
#include "Engine/ExponentialHeightFog.h"
#include "Components/ExponentialHeightFogComponent.h"

FKdkSkyState EvaluateSkyCycle(const FKdkSkyCycleParams& Params, float T)
{
	const float X = FMath::Clamp(T, 0.f, 1.f);
	const float S = X * X * (3.f - 2.f * X);
	FKdkSkyState State;
	State.Azimuth = FMath::Lerp(Params.StartAzimuth, Params.EndAzimuth, S);
	State.Elevation = FMath::Lerp(Params.StartElevation, Params.EndElevation, S);
	State.TemperatureK = FMath::Lerp(Params.StartTemperatureK, Params.EndTemperatureK, S);
	return State;
}

AKdkSkyCycleActor::AKdkSkyCycleActor()
{
	PrimaryActorTick.bCanEverTick = true;
	PrimaryActorTick.TickInterval = 0.5f;  // the sun moves a fraction of a degree per second; no need for per-frame updates
}

void AKdkSkyCycleActor::BeginPlay()
{
	Super::BeginPlay();
	float StartT = 0.f;
	if (Settings && FParse::Value(FCommandLine::Get(), TEXT("KdkSkyTime="), StartT))
	{
		ElapsedSeconds = FMath::Clamp(StartT, 0.f, 1.f) * Settings->Params.DurationMinutes * 60.f;
	}
	ApplyAt(Settings ? ElapsedSeconds / (Settings->Params.DurationMinutes * 60.f) : 0.f);
}

void AKdkSkyCycleActor::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	if (!Settings)
	{
		return;
	}
	ElapsedSeconds += DeltaSeconds;
	ApplyAt(ElapsedSeconds / (Settings->Params.DurationMinutes * 60.f));
}

void AKdkSkyCycleActor::ApplyAt(float T)
{
	if (!Settings || !Sun)
	{
		return;
	}
	FKdkSkyState State = EvaluateSkyCycle(Settings->Params, T);
	if (const UKdkGameUserSettings* U = UKdkGameUserSettings::Get())  // fog slider scales the level's fog density
	{
		for (TActorIterator<AExponentialHeightFog> It(GetWorld()); It; ++It)
		{
			UExponentialHeightFogComponent* Fog = It->GetComponent();
			if (BaseFog < 0.f) { BaseFog = Fog->FogDensity; }
			Fog->SetFogDensity(BaseFog * FMath::Clamp(U->FogAmount, 0.f, 3.f));
		}
	}
	const UKdkGameUserSettings* User = UKdkGameUserSettings::Get();
	const bool bDusk = User && User->bDusk;
	const float Dusk = bDusk ? FMath::Clamp(User->DuskAmount, 0.f, 1.f) : 0.f;
	if (bDusk)  // dusk mode: low warm sun skimming the hills, a fraction of the light
	{
		State.Elevation = FMath::Lerp(State.Elevation, 2.0f, Dusk);
		State.TemperatureK = FMath::Lerp(State.TemperatureK, 4200.f, Dusk);
	}
	// a directional light points away from the sun: pitch down by the elevation, yaw opposite to the azimuth
	Sun->SetActorRotation(FRotator(-State.Elevation, State.Azimuth + 180.f, 0.f));
	if (UDirectionalLightComponent* Light = Cast<UDirectionalLightComponent>(Sun->GetLightComponent()))
	{
		Light->SetUseTemperature(true);
		Light->SetTemperature(State.TemperatureK);
		if (BaseIntensity < 0.f)
		{
			BaseIntensity = Light->Intensity;
		}
		Light->SetIntensity(BaseIntensity * FMath::Lerp(1.f, 0.3f, Dusk));
		// auto exposure would brighten the dimmer scene back up; pull the exposure down so dusk really reads darker
		if (IConsoleVariable* Offset = IConsoleManager::Get().FindConsoleVariable(TEXT("r.ExposureOffset")))
		{
			Offset->Set(-1.5f * Dusk + (User ? User->Brightness : 0.f), ECVF_SetByCode);
		}
	}
}
