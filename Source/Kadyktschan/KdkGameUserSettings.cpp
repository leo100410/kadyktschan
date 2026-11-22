#include "KdkGameUserSettings.h"
#include "Engine/Engine.h"
#include "HAL/IConsoleManager.h"

UKdkGameUserSettings* UKdkGameUserSettings::Get()
{
	return GEngine ? Cast<UKdkGameUserSettings>(GEngine->GetGameUserSettings()) : nullptr;
}

void UKdkGameUserSettings::SetToDefaults()
{
	Super::SetToDefaults();
	MouseSensitivity = 1.f;
	bInvertMouseY = false;
	bHardwareRayTracing = false;
	bNanite = true;
	bShowFPS = false;
	bDusk = false;
}

void UKdkGameUserSettings::ApplyNonResolutionSettings()
{
	// the engine allows 0 % (an unreadable smear); the menu offers 25-100, older saves may hold less
	if (ScalabilityQuality.ResolutionQuality < MinRenderScale)
	{
		ScalabilityQuality.ResolutionQuality = 100.f;
	}
	Super::ApplyNonResolutionSettings();
	auto SetCVar = [](const TCHAR* Name, int32 Value)
	{
		if (IConsoleVariable* CVar = IConsoleManager::Get().FindConsoleVariable(Name))
		{
			CVar->Set(Value, ECVF_SetByGameSetting);
		}
	};
	// r.RayTracing.Enable also frees the ray tracing scene (needs r.RayTracing.EnableOnDemand=1 in DefaultEngine.ini)
	SetCVar(TEXT("r.RayTracing.Enable"), bHardwareRayTracing ? 1 : 0);
	SetCVar(TEXT("r.Lumen.HardwareRayTracing"), bHardwareRayTracing ? 1 : 0);
	SetCVar(TEXT("r.Nanite"), bNanite ? 1 : 0);
}

void UKdkGameUserSettings::SaveSettings()
{
	if (!TemporaryQualityOverride.IsSet())
	{
		Super::SaveSettings();
		return;
	}
	const Scalability::FQualityLevels Lowered = Scalability::GetQualityLevels();
	Scalability::SetQualityLevels(TemporaryQualityOverride.GetValue(), true);
	Super::SaveSettings();
	Scalability::SetQualityLevels(Lowered, true);
}
