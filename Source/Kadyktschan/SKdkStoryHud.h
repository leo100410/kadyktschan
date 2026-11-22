// Story overlay: the open objective (top left), the marker to the next goal with its distance, small rings on the
// finds close by, the "E - Ansehen" prompt, the reading panel and the notebook (N). Plain Slate; it only draws the
// snapshot AKadyktschanPlayerController fills every frame and takes no input (hit-test invisible).

#pragma once

#include "CoreMinimal.h"
#include "Widgets/SCompoundWidget.h"

struct FKdkHudState
{
	FString Header;        // "AUFGABE 2 / 6 · Brigadier Orlow (Lenina 7)"
	FString Goal;
	bool bMarker = false;
	FVector2f Marker = FVector2f::ZeroVector;  // viewport position, 0..1
	bool bMarkerOnScreen = false;
	float MarkerDistance = 0.f;                // metres
	TArray<FVector2f> Rings;                   // unread finds of the objective in sight, 0..1
	FString Prompt;                            // empty: nothing in focus
	FVector2f Focus = FVector2f::ZeroVector;
	bool bFocusRing = true;                    // false: Prompt is a message, not a thing in view (shooter mode)
	bool bStoryKeys = true;                    // the reading panel's "E / N" hint (the shooter mode has no notebook)
	bool bCrosshair = false;                   // shooter mode
	float CrosshairGap = 0.f;                  // half the spread cone, share of the view width
	float HitMarker = 0.f;                     // 1 right after a hit, fading out
	bool bKillMarker = false;
	float Aura = 0.f;                          // red edge, 0 at full health .. 1 when nearly down
	TArray<FVector3f> Threats;                 // where shots came from: screen direction (x right, y down) and alpha
	TArray<FVector3f> Marks;                   // enemies that just hit the player: viewport position 0..1 and alpha
	FString ReaderTitle;                       // empty: reading panel closed
	FString ReaderText;
	FString Notebook;                          // empty: notebook closed
};

class SKdkStoryHud : public SCompoundWidget
{
public:
	SLATE_BEGIN_ARGS(SKdkStoryHud) {}
		SLATE_ARGUMENT(TFunction<const FKdkHudState&()>, State)
	SLATE_END_ARGS()

	void Construct(const FArguments& InArgs);

	virtual int32 OnPaint(const FPaintArgs& Args, const FGeometry& AllottedGeometry, const FSlateRect& MyCullingRect,
		FSlateWindowElementList& OutDrawElements, int32 LayerId, const FWidgetStyle& InWidgetStyle, bool bParentEnabled) const override;

private:
	TFunction<const FKdkHudState&()> State;
};
