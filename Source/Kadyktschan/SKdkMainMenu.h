// Main menu shown at start (user 2026-11-09): the title picture (Content/Kadykchan/Data/UI/Title.png, made by
// tools/asset-pipeline/title_image.swift), the game's name, start, settings, language, quit. Plain Slate.

#pragma once

#include "CoreMinimal.h"
#include "Widgets/SCompoundWidget.h"

class SKdkMainMenu : public SCompoundWidget
{
public:
	SLATE_BEGIN_ARGS(SKdkMainMenu) {}
		/** The title picture (a brush over a texture the owner keeps alive); null shows a dark background. */
		SLATE_ARGUMENT(const FSlateBrush*, Picture)
		SLATE_EVENT(FSimpleDelegate, OnStart)
		/** Shooter mode "Einsatz" (design/gdd/shooter-mode.md). */
		SLATE_EVENT(FSimpleDelegate, OnShooter)
		SLATE_EVENT(FSimpleDelegate, OnSettings)
		/** The language was switched; the owner rebuilds the menu. */
		SLATE_EVENT(FSimpleDelegate, OnLanguage)
		SLATE_EVENT(FSimpleDelegate, OnQuit)
	SLATE_END_ARGS()

	void Construct(const FArguments& InArgs);
	virtual bool SupportsKeyboardFocus() const override { return true; }
};
