#include "SKdkMainMenu.h"

#include "KdkLoc.h"
#include "Brushes/SlateColorBrush.h"
#include "Styling/CoreStyle.h"
#include "Widgets/Images/SImage.h"
#include "Widgets/Input/SButton.h"
#include "Widgets/Layout/SBox.h"
#include "Widgets/Layout/SScaleBox.h"
#include "Widgets/SBoxPanel.h"
#include "Widgets/SOverlay.h"
#include "Widgets/Text/STextBlock.h"

namespace
{
	const FLinearColor Ink(0.92f, 0.90f, 0.84f);
	const FLinearColor Muted(0.62f, 0.62f, 0.58f);
	const FLinearColor Ember(0.95f, 0.62f, 0.38f);   // the sun in the title picture

	/** Text-only menu entry: grey, warm when hovered. */
	TSharedRef<SWidget> Entry(const FText& Label, FSimpleDelegate Click)
	{
		TSharedPtr<SButton> Button;
		SAssignNew(Button, SButton)
			.ButtonStyle(&FCoreStyle::Get().GetWidgetStyle<FButtonStyle>("NoBorder"))
			.OnClicked_Lambda([Click] { Click.ExecuteIfBound(); return FReply::Handled(); })
			.ContentPadding(FMargin(0.f, 6.f));
		TWeakPtr<SButton> Weak = Button;
		Button->SetContent(SNew(STextBlock).Text(Label).Font(FCoreStyle::GetDefaultFontStyle("Regular", 24))
			.ColorAndOpacity_Lambda([Weak] { return FSlateColor(Weak.IsValid() && Weak.Pin()->IsHovered() ? Ember : Ink); }));
		return Button.ToSharedRef();
	}
}

void SKdkMainMenu::Construct(const FArguments& InArgs)
{
	static const FSlateColorBrush Dark(FLinearColor(0.01f, 0.012f, 0.012f, 1.f));
	static const FSlateColorBrush Shade(FLinearColor(0.f, 0.f, 0.f, 0.55f));
	ChildSlot
	[
		SNew(SOverlay)
		+ SOverlay::Slot()
		[
			SNew(SImage).Image(&Dark)
		]
		+ SOverlay::Slot()
		[
			SNew(SScaleBox).Stretch(EStretch::ScaleToFill)
			[
				SNew(SImage).Image(InArgs._Picture ? InArgs._Picture : &Dark)
			]
		]
		// a dark band on the left keeps the menu readable over the sky
		+ SOverlay::Slot().HAlign(HAlign_Left)
		[
			SNew(SBox).WidthOverride(560.f)
			[
				SNew(SImage).Image(&Shade)
			]
		]
		+ SOverlay::Slot().HAlign(HAlign_Left).VAlign(VAlign_Center).Padding(80.f, 0.f)
		[
			SNew(SVerticalBox)
			+ SVerticalBox::Slot().AutoHeight()
			[
				SNew(STextBlock).Text(KdkLoc::T(TEXT("KADYKTSCHAN"), TEXT("KADYKCHAN"))).Font(FCoreStyle::GetDefaultFontStyle("Bold", 54)).ColorAndOpacity(Ink)
			]
			+ SVerticalBox::Slot().AutoHeight().Padding(4.f, 0.f, 0.f, 48.f)
			[
				SNew(STextBlock).Text(KdkLoc::T(TEXT("Колыма · Sommer 2011 · Eine verlassene Bergarbeiterstadt"), TEXT("Kolyma · summer 2011 · an abandoned mining town")))
					.Font(FCoreStyle::GetDefaultFontStyle("Regular", 15)).ColorAndOpacity(Muted)
			]
			+ SVerticalBox::Slot().AutoHeight()[ Entry(KdkLoc::T(TEXT("Spiel starten"), TEXT("Start game")), InArgs._OnStart) ]
			+ SVerticalBox::Slot().AutoHeight()[ Entry(KdkLoc::T(TEXT("Einsatz (Shooter)"), TEXT("Mission (shooter)")), InArgs._OnShooter) ]
			+ SVerticalBox::Slot().AutoHeight()[ Entry(KdkLoc::T(TEXT("Einstellungen"), TEXT("Settings")), InArgs._OnSettings) ]
			+ SVerticalBox::Slot().AutoHeight()[ Entry(KdkLoc::T(TEXT("Sprache: Deutsch"), TEXT("Language: English")), InArgs._OnLanguage) ]
			+ SVerticalBox::Slot().AutoHeight()[ Entry(KdkLoc::T(TEXT("Beenden"), TEXT("Quit")), InArgs._OnQuit) ]
		]
	];
}
