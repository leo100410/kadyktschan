// Two game languages without the localisation pipeline: every player-facing string is written as a German/English
// pair and picked by UKdkGameUserSettings::Language (user 2026-11-09: "bitte als Sprache Englisch hinzufügen").

#pragma once

#include "CoreMinimal.h"
#include "KdkGameUserSettings.h"

namespace KdkLoc
{
	inline bool IsEnglish()
	{
		const UKdkGameUserSettings* S = UKdkGameUserSettings::Get();
		return S && S->Language == TEXT("en");
	}

	/** The string for the current language. */
	inline FString S(const FString& De, const FString& En) { return IsEnglish() && !En.IsEmpty() ? En : De; }

	inline FText T(const TCHAR* De, const TCHAR* En) { return FText::FromString(IsEnglish() ? En : De); }
}
