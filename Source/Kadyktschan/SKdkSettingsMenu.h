// In-game settings menu (Esc / M): mouse and graphics. Plain Slate so it needs no widget blueprint.

#pragma once

#include "CoreMinimal.h"
#include "Widgets/SCompoundWidget.h"

class SKdkSettingsMenu : public SCompoundWidget
{
public:
	SLATE_BEGIN_ARGS(SKdkSettingsMenu) {}
		/** Called when the player closes the menu (button or Esc / M). */
		SLATE_EVENT(FSimpleDelegate, OnClose)
	SLATE_END_ARGS()

	void Construct(const FArguments& InArgs);

	virtual bool SupportsKeyboardFocus() const override { return true; }
	virtual FReply OnKeyDown(const FGeometry& MyGeometry, const FKeyEvent& InKeyEvent) override;

private:
	TSharedRef<SWidget> Heading(const FText& Text) const;
	/** Label, "<", current value, ">". Step receives -1 or +1. */
	TSharedRef<SWidget> CycleRow(const FText& Label, TFunction<FText()> Value, TFunction<void(int32)> Step) const;
	TSharedRef<SWidget> SliderRow(const FText& Label, TFunction<float()> GetNormalized, TFunction<void(float)> SetNormalized,
		TFunction<FText()> Value) const;

	FSimpleDelegate OnClose;
	TSharedPtr<class SScrollBox> ScrollList;
public:
	/** Remembers the scroll position so the menu reopens where it was left. */
	virtual ~SKdkSettingsMenu();
};
