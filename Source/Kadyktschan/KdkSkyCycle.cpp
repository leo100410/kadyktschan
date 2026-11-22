#include "KdkSkyCycle.h"
#include "Components/DirectionalLightComponent.h"
#include "Components/SkyLightComponent.h"
#include "Engine/SkyLight.h"
#include "Engine/DirectionalLight.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "HAL/IConsoleManager.h"
#include "KdkGameUserSettings.h"
#include "EngineUtils.h"
#include "Engine/ExponentialHeightFog.h"
#include "Components/ExponentialHeightFogComponent.h"

FKdkSkyState EvaluateSkyCycle(const FKdkSkyCycleParams& Params, float T, float DuskAmount)
{
	const float X = FMath::Clamp(T, 0.f, 1.f);
	const float S = X * X * (3.f - 2.f * X);
	FKdkSkyState State;
	State.Azimuth = FMath::Lerp(Params.StartAzimuth, Params.EndAzimuth, S);
	State.Elevation = FMath::Lerp(Params.StartElevation, Params.EndElevation, S);
	State.TemperatureK = FMath::Lerp(Params.StartTemperatureK, Params.EndTemperatureK, S);
	const float Dusk = FMath::Clamp(DuskAmount, 0.f, 1.f);
	State.Elevation = FMath::Lerp(State.Elevation, -4.f, Dusk);
	State.TemperatureK = FMath::Lerp(State.TemperatureK, 4200.f, Dusk);
	State.SunIntensityScale = FMath::Lerp(1.f, 0.03f, Dusk);
	State.SkyIntensityScale = FMath::Lerp(1.f, 0.04f, Dusk);
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
	FParse::Value(FCommandLine::Get(), TEXT("KdkSkySpeed="), TimeScale);  // dev: run the cycle faster to test shadow updates
	ApplyAt(Settings ? ElapsedSeconds / (Settings->Params.DurationMinutes * 60.f) : 0.f);
	UE_LOG(LogTemp, Log, TEXT("KdkSky: sun %s"), Sun ? *Sun->GetActorRotation().ToString() : TEXT("none"));
}

void AKdkSkyCycleActor::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	if (!Settings)
	{
		return;
	}
	ElapsedSeconds += DeltaSeconds * TimeScale;
	ApplyAt(ElapsedSeconds / (Settings->Params.DurationMinutes * 60.f));
}

void AKdkSkyCycleActor::ApplyAt(float T)
{
	if (!Settings || !Sun)
	{
		return;
	}
	const UKdkGameUserSettings* User = UKdkGameUserSettings::Get();
	const float Dusk = User && User->bDusk ? FMath::Clamp(User->DuskAmount, 0.f, 1.f) : 0.f;
	const FKdkSkyState State = EvaluateSkyCycle(Settings->Params, T, Dusk);
	for (TActorIterator<ASkyLight> It(GetWorld()); It; ++It)
	{
		USkyLightComponent* Sky = It->GetLightComponent();
		if (BaseSkyIntensity < 0.f) BaseSkyIntensity = Sky->Intensity;
		Sky->SetIntensity(BaseSkyIntensity * State.SkyIntensityScale);
	}
	for (TActorIterator<AExponentialHeightFog> It(GetWorld()); It; ++It)
	{
		UExponentialHeightFogComponent* Fog = It->GetComponent();
		if (BaseFog < 0.f) BaseFog = Fog->FogDensity;
		if (BaseFogLuminance.R < 0.f) BaseFogLuminance = Fog->FogInscatteringLuminance;
		Fog->SetFogDensity(BaseFog * (User ? FMath::Clamp(User->FogAmount, 0.f, 3.f) : 1.f));
		Fog->SetFogInscatteringColor(BaseFogLuminance * FMath::Lerp(1.f, 0.15f, Dusk));
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
		Light->SetIntensity(BaseIntensity * State.SunIntensityScale);
		// auto exposure would brighten the dimmer scene back up; pull the exposure down so dusk really reads darker
		if (IConsoleVariable* Offset = IConsoleManager::Get().FindConsoleVariable(TEXT("r.ExposureOffset")))
		{
			Offset->Set(-1.5f * Dusk + (User ? User->Brightness : 0.f), ECVF_SetByCode);
		}
	}
}
