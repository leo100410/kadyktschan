#include "SKdkStoryHud.h"

#include "Brushes/SlateRoundedBoxBrush.h"
#include "Rendering/DrawElements.h"
#include "Styling/CoreStyle.h"
#include "Widgets/Layout/SBorder.h"
#include "Widgets/Layout/SBox.h"
#include "Widgets/SBoxPanel.h"
#include "Widgets/SOverlay.h"
#include "Widgets/Text/STextBlock.h"
#include "KdkLoc.h"

namespace
{
	// warm paper-ink tones that sit on a dark interior without glaring (same family as the town map)
	const FLinearColor Ink(0.92f, 0.90f, 0.84f);
	const FLinearColor Muted(0.62f, 0.62f, 0.58f);
	const FLinearColor Accent(0.95f, 0.72f, 0.30f);   // marker and rings: the torch's yellow
	const FSlateBrush* Panel()
	{
		static const FSlateRoundedBoxBrush Brush(FLinearColor(0.02f, 0.022f, 0.02f, 0.86f), 6.f);
		return &Brush;
	}
	const FSlateBrush* Chip()
	{
		static const FSlateRoundedBoxBrush Brush(FLinearColor(0.02f, 0.022f, 0.02f, 0.7f), 4.f);
		return &Brush;
	}

	void Ring(FSlateWindowElementList& Out, int32 Layer, const FGeometry& G, FVector2f C, float R, const FLinearColor& Col, float Thick)
	{
		TArray<FVector2f> Pts;
		for (int32 K = 0; K <= 24; ++K)
		{
			const float A = 2.f * PI * K / 24.f;
			Pts.Add(C + FVector2f(FMath::Cos(A), FMath::Sin(A)) * R);
		}
		FSlateDrawElement::MakeLines(Out, Layer, G.ToPaintGeometry(), Pts, ESlateDrawEffect::None, Col, true, Thick);
	}
}

void SKdkStoryHud::Construct(const FArguments& InArgs)
{
	State = InArgs._State;
	auto Get = [this]() -> const FKdkHudState& { return State(); };
	auto Shown = [Get](TFunction<bool(const FKdkHudState&)> Test)
	{
		return TAttribute<EVisibility>::CreateLambda([Get, Test]() { return Test(Get()) ? EVisibility::HitTestInvisible : EVisibility::Collapsed; });
	};
	auto Text = [Get](FString FKdkHudState::*Field)
	{
		return TAttribute<FText>::CreateLambda([Get, Field]() { return FText::FromString(Get().*Field); });
	};
	SetVisibility(EVisibility::HitTestInvisible);

	ChildSlot
	[
		SNew(SOverlay)
		// objective, top left
		+ SOverlay::Slot().HAlign(HAlign_Left).VAlign(VAlign_Top).Padding(28.f, 24.f)
		[
			SNew(SBox).MaxDesiredWidth(470.f).Visibility(Shown([](const FKdkHudState& S) { return !S.Goal.IsEmpty(); }))
			[
				SNew(SBorder).BorderImage(Chip()).Padding(FMargin(14.f, 10.f))
				[
					SNew(SVerticalBox)
					+ SVerticalBox::Slot().AutoHeight()
					[
						SNew(STextBlock).Text(Text(&FKdkHudState::Header)).Font(FCoreStyle::GetDefaultFontStyle("Bold", 11)).ColorAndOpacity(Accent)
					]
					+ SVerticalBox::Slot().AutoHeight().Padding(0.f, 4.f, 0.f, 0.f)
					[
						SNew(STextBlock).Text(Text(&FKdkHudState::Goal)).AutoWrapText(true).Font(FCoreStyle::GetDefaultFontStyle("Regular", 13)).ColorAndOpacity(Ink)
					]
				]
			]
		]
		// prompt, below the screen centre
		+ SOverlay::Slot().HAlign(HAlign_Center).VAlign(VAlign_Center).Padding(0.f, 150.f, 0.f, 0.f)
		[
			SNew(SBorder).BorderImage(Chip()).Padding(FMargin(12.f, 6.f))
			.Visibility(Shown([](const FKdkHudState& S) { return !S.Prompt.IsEmpty() && S.ReaderTitle.IsEmpty() && S.Notebook.IsEmpty(); }))
			[
				SNew(STextBlock).Text(Text(&FKdkHudState::Prompt)).Font(FCoreStyle::GetDefaultFontStyle("Regular", 14)).ColorAndOpacity(Ink)
			]
		]
		// reading panel
		+ SOverlay::Slot().HAlign(HAlign_Center).VAlign(VAlign_Center)
		[
			SNew(SBox).WidthOverride(620.f).Visibility(Shown([](const FKdkHudState& S) { return !S.ReaderTitle.IsEmpty(); }))
			[
				SNew(SBorder).BorderImage(Panel()).Padding(FMargin(28.f, 22.f))
				[
					SNew(SVerticalBox)
					+ SVerticalBox::Slot().AutoHeight()
					[
						SNew(STextBlock).Text(Text(&FKdkHudState::ReaderTitle)).Font(FCoreStyle::GetDefaultFontStyle("Bold", 20)).ColorAndOpacity(Accent)
					]
					+ SVerticalBox::Slot().AutoHeight().Padding(0.f, 14.f)
					[
						SNew(STextBlock).Text(Text(&FKdkHudState::ReaderText)).AutoWrapText(true).Font(FCoreStyle::GetDefaultFontStyle("Regular", 15)).ColorAndOpacity(Ink)
					]
					+ SVerticalBox::Slot().AutoHeight()
					[
						SNew(STextBlock).Text_Lambda([] { return KdkLoc::T(TEXT("E: schließen   ·   N: Notizbuch"), TEXT("E: close   ·   N: notebook")); }).Font(FCoreStyle::GetDefaultFontStyle("Regular", 11)).ColorAndOpacity(Muted)
							.Visibility(Shown([](const FKdkHudState& S) { return S.bStoryKeys; }))
					]
				]
			]
		]
		// notebook
		+ SOverlay::Slot().HAlign(HAlign_Center).VAlign(VAlign_Center)
		[
			SNew(SBox).WidthOverride(700.f).Visibility(Shown([](const FKdkHudState& S) { return !S.Notebook.IsEmpty(); }))
			[
				SNew(SBorder).BorderImage(Panel()).Padding(FMargin(28.f, 22.f))
				[
					SNew(SVerticalBox)
					+ SVerticalBox::Slot().AutoHeight()
					[
						SNew(STextBlock).Text_Lambda([] { return KdkLoc::T(TEXT("Notizbuch"), TEXT("Notebook")); }).Font(FCoreStyle::GetDefaultFontStyle("Bold", 20)).ColorAndOpacity(Accent)
					]
					+ SVerticalBox::Slot().AutoHeight().Padding(0.f, 14.f)
					[
						SNew(STextBlock).Text(Text(&FKdkHudState::Notebook)).AutoWrapText(true).Font(FCoreStyle::GetDefaultFontStyle("Regular", 13)).ColorAndOpacity(Ink)
					]
					+ SVerticalBox::Slot().AutoHeight()
					[
						SNew(STextBlock).Text_Lambda([] { return KdkLoc::T(TEXT("N: schließen"), TEXT("N: close")); }).Font(FCoreStyle::GetDefaultFontStyle("Regular", 11)).ColorAndOpacity(Muted)
					]
				]
			]
		]
	];
}

int32 SKdkStoryHud::OnPaint(const FPaintArgs& Args, const FGeometry& G, const FSlateRect& MyCullingRect,
	FSlateWindowElementList& Out, int32 LayerId, const FWidgetStyle& InWidgetStyle, bool bParentEnabled) const
{
	const FKdkHudState& S = State();
	const FVector2f Size = G.GetLocalSize();
	const bool bPanel = !S.ReaderTitle.IsEmpty() || !S.Notebook.IsEmpty();
	if (!bPanel)
	{
		const float Pulse = 0.65f + 0.35f * FMath::Sin(FPlatformTime::Seconds() * 3.0);
		for (const FVector2f& R : S.Rings)
		{
			Ring(Out, LayerId, G, R * Size, 9.f, Accent.CopyWithNewOpacity(0.55f * Pulse), 1.5f);
		}
		if (S.Aura > 0.02f)
		{
			// red aura: nested frames from the screen edge inwards, wider and stronger the more health is lost
			const int32 Rings = 16;
			const float Depth = S.Aura * 0.24f * FMath::Min(Size.X, Size.Y);
			const float Step = Depth / Rings;
			for (int32 I = 0; I < Rings; ++I)
			{
				const float In = Step * (I + 0.5f);
				const float A = 0.55f * S.Aura * FMath::Pow(1.f - float(I) / Rings, 1.6f);
				const TArray<FVector2f> Frame = {FVector2f(In, In), FVector2f(Size.X - In, In), FVector2f(Size.X - In, Size.Y - In), FVector2f(In, Size.Y - In), FVector2f(In, In)};
				FSlateDrawElement::MakeLines(Out, LayerId, G.ToPaintGeometry(), Frame, ESlateDrawEffect::None, FLinearColor(0.7f, 0.02f, 0.02f, A), false, Step + 1.f);
			}
		}
		for (const FVector3f& T : S.Threats)
		{
			// where the shot came from: a red arc around the centre, like the damage indicator in Fortnite
			const FVector2f C = Size * 0.5f;
			const float R = 0.24f * Size.Y;
			const float Mid = FMath::Atan2(T.Y, T.X);
			TArray<FVector2f> Arc;
			for (int32 K = 0; K <= 10; ++K)
			{
				const float A = Mid + FMath::DegreesToRadians(-20.f + 4.f * K);
				Arc.Add(C + FVector2f(FMath::Cos(A), FMath::Sin(A)) * R);
			}
			FSlateDrawElement::MakeLines(Out, LayerId, G.ToPaintGeometry(), Arc, ESlateDrawEffect::None, FLinearColor(0.95f, 0.12f, 0.08f, T.Z), true, 10.f);
			const FVector2f Tip = C + FVector2f(FMath::Cos(Mid), FMath::Sin(Mid)) * (R + 24.f);
			const FVector2f Side(-FMath::Sin(Mid), FMath::Cos(Mid));
			FSlateDrawElement::MakeLines(Out, LayerId, G.ToPaintGeometry(), {Arc[3] + (Arc[3] - C).GetSafeNormal() * 5.f, Tip, Arc[7] + (Arc[7] - C).GetSafeNormal() * 5.f},
				ESlateDrawEffect::None, FLinearColor(0.95f, 0.12f, 0.08f, T.Z), true, 4.f);
		}
		for (const FVector3f& M : S.Marks)
		{
			// the enemy that just hit you: a red ring with a point down onto its head, also through walls
			const FVector2f C = FVector2f(M.X, M.Y) * Size;
			const FLinearColor Red(0.95f, 0.15f, 0.1f, M.Z);
			Ring(Out, LayerId, G, C, 13.f, Red, 3.f);
			FSlateDrawElement::MakeLines(Out, LayerId, G.ToPaintGeometry(), {C + FVector2f(-9.f, 16.f), C + FVector2f(0.f, 28.f), C + FVector2f(9.f, 16.f)},
				ESlateDrawEffect::None, Red, true, 3.f);
		}
		if (S.bCrosshair)
		{
			// four ticks around the centre; the gap shows the spread (tight aimed, wide running)
			const FVector2f C = Size * 0.5f;
			const float Gap = FMath::Clamp(S.CrosshairGap * Size.X, 7.f, 80.f);
			const FLinearColor Col = Ink.CopyWithNewOpacity(0.95f);
			const FLinearColor Edge(0.f, 0.f, 0.f, 0.6f);  // dark outline: readable against the white-night sky
			for (const FVector2f D : {FVector2f(1, 0), FVector2f(-1, 0), FVector2f(0, 1), FVector2f(0, -1)})
			{
				FSlateDrawElement::MakeLines(Out, LayerId, G.ToPaintGeometry(), {C + D * (Gap - 1.f), C + D * (Gap + 17.f)}, ESlateDrawEffect::None, Edge, true, 5.f);
				FSlateDrawElement::MakeLines(Out, LayerId, G.ToPaintGeometry(), {C + D * Gap, C + D * (Gap + 16.f)}, ESlateDrawEffect::None, Col, true, 2.5f);
			}
			if (S.HitMarker > 0.f)  // hit: a diagonal cross outside the ticks
			{
				const FLinearColor Mark = (S.bKillMarker ? FLinearColor(0.95f, 0.22f, 0.15f) : FLinearColor::White).CopyWithNewOpacity(S.HitMarker);
				for (const FVector2f D : {FVector2f(1, 1), FVector2f(-1, 1), FVector2f(1, -1), FVector2f(-1, -1)})
				{
					const FVector2f N = D.GetSafeNormal();
					FSlateDrawElement::MakeLines(Out, LayerId, G.ToPaintGeometry(), {C + N * (Gap + 6.f), C + N * (Gap + 22.f)}, ESlateDrawEffect::None, Mark, true, 3.5f);
				}
			}
		}
		if (!S.Prompt.IsEmpty() && S.bFocusRing)
		{
			Ring(Out, LayerId, G, S.Focus * Size, 15.f, Accent, 2.f);
		}
		if (S.bMarker)
		{
			// a diamond with the distance under it; at the screen edge it points the way
			const FVector2f C = S.Marker * Size;
			const float R = S.bMarkerOnScreen ? 11.f : 14.f;
			TArray<FVector2f> D = {C + FVector2f(0, -R), C + FVector2f(R, 0), C + FVector2f(0, R), C + FVector2f(-R, 0), C + FVector2f(0, -R)};
			FSlateDrawElement::MakeLines(Out, LayerId, G.ToPaintGeometry(), D, ESlateDrawEffect::None, Accent, true, 2.5f);
			const FString Dist = FString::Printf(TEXT("%d m"), FMath::RoundToInt(S.MarkerDistance));
			FSlateDrawElement::MakeText(Out, LayerId, G.ToPaintGeometry(FVector2f(80.f, 20.f), FSlateLayoutTransform(C + FVector2f(-14.f, R + 4.f))),
				Dist, FCoreStyle::GetDefaultFontStyle("Bold", 11), ESlateDrawEffect::None, Accent);
		}
	}
	return SCompoundWidget::OnPaint(Args, G, MyCullingRect, Out, LayerId + 1, InWidgetStyle, bParentEnabled);
}
