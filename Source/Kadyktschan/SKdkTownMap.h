// In-game town plan (K / Tab): footprints, roads, the furnished houses and where the player stands. Plain Slate,
// drawn from Content/Kadykchan/Data/TownMap.json (written by tools/research/town_map_data.py).

#pragma once

#include "CoreMinimal.h"
#include "Widgets/SLeafWidget.h"

class SKdkTownMap : public SLeafWidget
{
public:
	SLATE_BEGIN_ARGS(SKdkTownMap) : _Detailed(false) {}
		/** Player position in town metres (X = east, Y = north) and view yaw in degrees (0 = north, 90 = east). */
		SLATE_ARGUMENT(TFunction<FVector3f()>, PlayerView)
		SLATE_ARGUMENT(bool, Detailed)
		SLATE_EVENT(FSimpleDelegate, OnClose)
	SLATE_END_ARGS()

	void Construct(const FArguments& InArgs);

	virtual int32 OnPaint(const FPaintArgs& Args, const FGeometry& AllottedGeometry, const FSlateRect& MyCullingRect,
		FSlateWindowElementList& OutDrawElements, int32 LayerId, const FWidgetStyle& InWidgetStyle, bool bParentEnabled) const override;
	virtual FVector2D ComputeDesiredSize(float) const override { return FVector2D(800.0, 600.0); }

	/** Loads the plan; false (and an empty map) when the data file is missing or malformed. */
	static bool LoadPlan(const FString& Json, struct FKdkTownPlan& Out);
	static TArray<FVector2f> LayoutMarkers(const TArray<FVector2f>& Anchors, const FBox2f& Area);
	virtual bool SupportsKeyboardFocus() const override { return bDetailed; }
	virtual FReply OnKeyDown(const FGeometry& Geometry, const FKeyEvent& Event) override;
	virtual FReply OnMouseButtonDown(const FGeometry& Geometry, const FPointerEvent& Event) override;

private:
	TFunction<FVector3f()> PlayerView;
	TSharedPtr<struct FKdkTownPlan> Plan;
	bool bDetailed = false;
	FSimpleDelegate OnClose;
};

struct FKdkTownPlace
{
	FString Name;
	FString NameEn;  // English label (empty: the German one)
	bool bStory = false;
	int32 Floors = 0;
	FString Details, DetailsEn;
	FVector2f Entry = FVector2f::ZeroVector;
	FVector2f Pos = FVector2f::ZeroVector;  // building centre, metres east/north
};

struct FKdkTownPlan
{
	/** Footprint rectangles: centre (east, north), length, width, axis angle (degrees from east, counter-clockwise). */
	struct FBuilding { FVector2f Centre; float Length, Width, AxisDeg; };
	TArray<FBuilding> Buildings;
	TArray<TArray<FVector2f>> Roads;
	TArray<TArray<FVector2f>> Rivers;
	TArray<FKdkTownPlace> Places;
	FBox2f Bounds = FBox2f(ForceInit);
};
