#include "SKdkSettingsMenu.h"
#include "KdkGameUserSettings.h"
#include "Framework/Application/SlateApplication.h"
#include "Styling/CoreStyle.h"
#include "Widgets/Input/SButton.h"
#include "Widgets/Input/SSlider.h"
#include "Widgets/Layout/SBorder.h"
#include "Widgets/Layout/SBox.h"
#include "Widgets/Layout/SScrollBox.h"
#include "Widgets/Text/STextBlock.h"

#include "KdkLoc.h"
#define LOCTEXT_NAMESPACE "KdkSettings"

namespace
{
	FSlateFontInfo Font(int32 Size) { return FCoreStyle::GetDefaultFontStyle("Regular", Size); }

	FText QualityText(int32 Level)
	{
		switch (Level)
		{
		case 0: return KdkLoc::T(TEXT("Niedrig"), TEXT("Low"));
		case 1: return KdkLoc::T(TEXT("Mittel"), TEXT("Medium"));
		case 2: return KdkLoc::T(TEXT("Hoch"), TEXT("High"));
		case 3: return KdkLoc::T(TEXT("Episch"), TEXT("Epic"));
		case 4: return KdkLoc::T(TEXT("Kino"), TEXT("Cinematic"));
		default: return KdkLoc::T(TEXT("Benutzerdefiniert"), TEXT("Custom"));
		}
	}

	FText OnOff(bool b) { return b ? KdkLoc::T(TEXT("An"), TEXT("On")) : KdkLoc::T(TEXT("Aus"), TEXT("Off")); }

	int32 StepQuality(int32 Level, int32 Dir) { return FMath::Clamp(Level + Dir, 0, 4); }

	/** Every change is applied at once so the player sees the effect behind the menu; saved on close. */
	void Apply(UKdkGameUserSettings* S) { S->ApplyNonResolutionSettings(); }

	const float FrameLimits[] = { 30.f, 60.f, 120.f, 0.f };
	float SavedScroll = 0.f;  // survives closing and reopening the menu
}

void SKdkSettingsMenu::Construct(const FArguments& InArgs)
{
	OnClose = InArgs._OnClose;
	UKdkGameUserSettings* S = UKdkGameUserSettings::Get();
	check(S);

	// one row per scalability group: {label, getter, setter}
	struct FGroup { FText Label; int32 (UGameUserSettings::*Get)() const; void (UGameUserSettings::*Set)(int32); };
	const FGroup Groups[] = {
		{ KdkLoc::T(TEXT("Sichtweite"), TEXT("View distance")), &UGameUserSettings::GetViewDistanceQuality, &UGameUserSettings::SetViewDistanceQuality },
		{ KdkLoc::T(TEXT("Schatten"), TEXT("Shadows")), &UGameUserSettings::GetShadowQuality, &UGameUserSettings::SetShadowQuality },
		{ KdkLoc::T(TEXT("Globale Beleuchtung"), TEXT("Global illumination")), &UGameUserSettings::GetGlobalIlluminationQuality, &UGameUserSettings::SetGlobalIlluminationQuality },
		{ KdkLoc::T(TEXT("Reflexionen"), TEXT("Reflections")), &UGameUserSettings::GetReflectionQuality, &UGameUserSettings::SetReflectionQuality },
		{ KdkLoc::T(TEXT("Texturen"), TEXT("Textures")), &UGameUserSettings::GetTextureQuality, &UGameUserSettings::SetTextureQuality },
		{ KdkLoc::T(TEXT("Effekte"), TEXT("Effects")), &UGameUserSettings::GetVisualEffectQuality, &UGameUserSettings::SetVisualEffectQuality },
		{ KdkLoc::T(TEXT("Vegetation"), TEXT("Vegetation")), &UGameUserSettings::GetFoliageQuality, &UGameUserSettings::SetFoliageQuality },
		{ KdkLoc::T(TEXT("Nachbearbeitung"), TEXT("Post-processing")), &UGameUserSettings::GetPostProcessingQuality, &UGameUserSettings::SetPostProcessingQuality },
		{ KdkLoc::T(TEXT("Kantenglättung"), TEXT("Anti-aliasing")), &UGameUserSettings::GetAntiAliasingQuality, &UGameUserSettings::SetAntiAliasingQuality },
		{ KdkLoc::T(TEXT("Materialqualität"), TEXT("Material quality")), &UGameUserSettings::GetShadingQuality, &UGameUserSettings::SetShadingQuality },
	};

	TSharedRef<SScrollBox> List = SNew(SScrollBox);
	ScrollList = List;
	auto Add = [&List](TSharedRef<SWidget> W) { List->AddSlot().Padding(0, 3)[W]; };

	const FSimpleDelegate Map = InArgs._OnFurnishingMap;
	Add(SNew(SButton).OnClicked_Lambda([Map]() { Map.ExecuteIfBound(); return FReply::Handled(); })
		[SNew(STextBlock).Font(Font(16)).Text(KdkLoc::T(TEXT("Einrichtungskarte öffnen"),TEXT("Open furnishing map")))]);
	// language first: switching rebuilds the menu (OnLanguage) so every label follows at once
	FSimpleDelegate Relabel = InArgs._OnLanguage;
	Add(CycleRow(KdkLoc::T(TEXT("Sprache"), TEXT("Language")), [] { return FText::FromString(KdkLoc::IsEnglish() ? TEXT("English") : TEXT("Deutsch")); },
		[S, Relabel](int32) { S->Language = KdkLoc::IsEnglish() ? TEXT("de") : TEXT("en"); S->SaveSettings(); Relabel.ExecuteIfBound(); }));
	Add(Heading(KdkLoc::T(TEXT("Maus"), TEXT("Mouse"))));
	Add(SliderRow(KdkLoc::T(TEXT("Empfindlichkeit"), TEXT("Sensitivity")),
		[S] { return (S->MouseSensitivity - 0.1f) / 2.9f; },
		[S](float N) { S->MouseSensitivity = FMath::RoundToFloat((0.1f + N * 2.9f) * 20.f) / 20.f; },
		[S] { return FText::AsNumber(S->MouseSensitivity); }));
	Add(CycleRow(KdkLoc::T(TEXT("Maus-Y umkehren"), TEXT("Invert mouse Y")), [S] { return OnOff(S->bInvertMouseY); },
		[S](int32) { S->bInvertMouseY = !S->bInvertMouseY; }));

	Add(Heading(KdkLoc::T(TEXT("Grafik"), TEXT("Graphics"))));
	Add(CycleRow(KdkLoc::T(TEXT("Gesamtqualität"), TEXT("Overall quality")), [S] { return QualityText(S->GetOverallScalabilityLevel()); },
		[S](int32 Dir) { S->SetOverallScalabilityLevel(StepQuality(FMath::Max(S->GetOverallScalabilityLevel(), 1), Dir)); Apply(S); }));
	Add(SliderRow(KdkLoc::T(TEXT("Renderauflösung"), TEXT("Render resolution")),
		[S] { float N, V, Min, Max; S->GetResolutionScaleInformationEx(N, V, Min, Max);
			return FMath::Clamp((V - UKdkGameUserSettings::MinRenderScale) / (100.f - UKdkGameUserSettings::MinRenderScale), 0.f, 1.f); },
		[S](float N) { S->SetResolutionScaleValueEx(FMath::RoundToFloat(FMath::Lerp(UKdkGameUserSettings::MinRenderScale, 100.f, N) / 5.f) * 5.f); Apply(S); },
		[S] { float N, V, Min, Max; S->GetResolutionScaleInformationEx(N, V, Min, Max); return FText::Format(KdkLoc::T(TEXT("{0} %"), TEXT("{0} %")), FText::AsNumber(FMath::RoundToInt(V))); }));
	for (const FGroup& G : Groups)
	{
		Add(CycleRow(G.Label, [S, G] { return QualityText((S->*G.Get)()); },
			[S, G](int32 Dir) { (S->*G.Set)(StepQuality((S->*G.Get)(), Dir)); Apply(S); }));
	}
	Add(CycleRow(KdkLoc::T(TEXT("Raytracing (Hardware)"), TEXT("Ray tracing (hardware)")), [S] { return OnOff(S->bHardwareRayTracing); },
		[S](int32) { S->bHardwareRayTracing = !S->bHardwareRayTracing; Apply(S); }));
	Add(CycleRow(KdkLoc::T(TEXT("Nanite"), TEXT("Nanite")), [S] { return OnOff(S->bNanite); },
		[S](int32) { S->bNanite = !S->bNanite; Apply(S); }));

	Add(Heading(KdkLoc::T(TEXT("Anzeige"), TEXT("Display"))));
	Add(CycleRow(KdkLoc::T(TEXT("Fenstermodus"), TEXT("Window mode")),
		[S]
		{
			switch (S->GetFullscreenMode())
			{
			case EWindowMode::Fullscreen: return KdkLoc::T(TEXT("Vollbild"), TEXT("Fullscreen"));
			case EWindowMode::WindowedFullscreen: return KdkLoc::T(TEXT("Vollbild (Fenster)"), TEXT("Fullscreen (windowed)"));
			default: return KdkLoc::T(TEXT("Fenster"), TEXT("Windowed"));
			}
		},
		[S](int32 Dir)
		{
			const int32 Mode = (static_cast<int32>(S->GetFullscreenMode()) + Dir + EWindowMode::NumWindowModes) % EWindowMode::NumWindowModes;
			S->SetFullscreenMode(EWindowMode::ConvertIntToWindowMode(Mode));
			if (Mode != EWindowMode::Windowed)
			{
				S->SetScreenResolution(S->GetDesktopResolution());
			}
			S->ApplyResolutionSettings(false);
		}));
	Add(CycleRow(KdkLoc::T(TEXT("VSync"), TEXT("VSync")), [S] { return OnOff(S->IsVSyncEnabled()); },
		[S](int32) { S->SetVSyncEnabled(!S->IsVSyncEnabled()); Apply(S); }));
	Add(CycleRow(KdkLoc::T(TEXT("Bildrate-Limit"), TEXT("Frame rate limit")),
		[S] { const float L = S->GetFrameRateLimit(); return L <= 0.f ? KdkLoc::T(TEXT("Unbegrenzt"), TEXT("Unlimited")) : FText::AsNumber(FMath::RoundToInt(L)); },
		[S](int32 Dir)
		{
			int32 Index = UE_ARRAY_COUNT(FrameLimits) - 1;
			for (int32 i = 0; i < UE_ARRAY_COUNT(FrameLimits); ++i)
			{
				if (FMath::IsNearlyEqual(FrameLimits[i], S->GetFrameRateLimit())) { Index = i; }
			}
			Index = (Index + Dir + UE_ARRAY_COUNT(FrameLimits)) % UE_ARRAY_COUNT(FrameLimits);
			S->SetFrameRateLimit(FrameLimits[Index]);
			Apply(S);
		}));
	Add(CycleRow(KdkLoc::T(TEXT("Videokamera"), TEXT("Camcorder")), [S] { return OnOff(S->bCamcorder); },
		[S](int32) { S->bCamcorder = !S->bCamcorder; }));  // applied by the player controller
	Add(SliderRow(KdkLoc::T(TEXT("Helligkeit"), TEXT("Brightness")), [S] { return (S->Brightness + 2.f) / 4.f; },
		[S](float N) { S->Brightness = FMath::RoundToFloat((N * 4.f - 2.f) * 10.f) / 10.f; },
		[S] { return FText::AsNumber(S->Brightness); }));
	Add(SliderRow(KdkLoc::T(TEXT("Dämmerungsstärke"), TEXT("Dusk strength")), [S] { return S->DuskAmount; },
		[S](float N) { S->DuskAmount = FMath::RoundToFloat(N * 20.f) / 20.f; },
		[S] { return FText::Format(KdkLoc::T(TEXT("{0} %"), TEXT("{0} %")), FText::AsNumber(FMath::RoundToInt(S->DuskAmount * 100))); }));
	Add(SliderRow(KdkLoc::T(TEXT("Verpixelung (Videokamera)"), TEXT("Pixelation (camcorder)")), [S] { return S->CamPixelation; },
		[S](float N) { S->CamPixelation = FMath::RoundToFloat(N * 20.f) / 20.f; },
		[S] { return FText::Format(KdkLoc::T(TEXT("{0} %"), TEXT("{0} %")), FText::AsNumber(FMath::RoundToInt(S->CamPixelation * 100))); }));
	Add(SliderRow(KdkLoc::T(TEXT("Stärke (Videokamera)"), TEXT("Strength (camcorder)")), [S] { return S->CamNoise; },
		[S](float N) { S->CamNoise = FMath::RoundToFloat(N * 20.f) / 20.f; },
		[S] { return FText::Format(KdkLoc::T(TEXT("{0} %"), TEXT("{0} %")), FText::AsNumber(FMath::RoundToInt(S->CamNoise * 100))); }));
	Add(SliderRow(KdkLoc::T(TEXT("Nebel"), TEXT("Fog")), [S] { return S->FogAmount / 3.f; },
		[S](float N) { S->FogAmount = FMath::RoundToFloat(N * 30.f) / 10.f; },
		[S] { return FText::Format(KdkLoc::T(TEXT("{0} %"), TEXT("{0} %")), FText::AsNumber(FMath::RoundToInt(S->FogAmount * 100))); }));
	Add(CycleRow(KdkLoc::T(TEXT("Dämmerung"), TEXT("Dusk")), [S] { return OnOff(S->bDusk); },
		[S](int32) { S->bDusk = !S->bDusk; }));  // the sky cycle actor reads it on its next tick
	Add(CycleRow(KdkLoc::T(TEXT("Bilder pro Sekunde anzeigen"), TEXT("Show frames per second")), [S] { return OnOff(S->bShowFPS); },
		[S](int32) { S->bShowFPS = !S->bShowFPS; if (GEngine) { GEngine->Exec(nullptr, TEXT("stat fps")); } }));

	List->SetScrollOffset(SavedScroll);
	ChildSlot
	[
		SNew(SBorder)
		.BorderImage(FCoreStyle::Get().GetBrush("WhiteBrush"))
		.BorderBackgroundColor(FLinearColor(0.f, 0.f, 0.f, 0.55f))
		.HAlign(HAlign_Center).VAlign(VAlign_Center)
		[
			SNew(SBox).WidthOverride(640.f).MaxDesiredHeight(860.f)
			[
				SNew(SBorder)
				.BorderImage(FCoreStyle::Get().GetBrush("WhiteBrush"))
				.BorderBackgroundColor(FLinearColor(0.035f, 0.04f, 0.045f, 0.96f))
				.Padding(28.f)
				[
					SNew(SVerticalBox)
					+ SVerticalBox::Slot().AutoHeight().Padding(0, 0, 0, 12)
					[
						SNew(STextBlock).Font(Font(26)).Text(KdkLoc::T(TEXT("Einstellungen"), TEXT("Settings")))
					]
					+ SVerticalBox::Slot().FillHeight(1.f)
					[
						List
					]
					+ SVerticalBox::Slot().AutoHeight().Padding(0, 12, 0, 0)
					[
						SNew(STextBlock).Font(Font(13)).ColorAndOpacity(FLinearColor(0.62f, 0.68f, 0.72f)).AutoWrapText(true)
						.Text(KdkLoc::T(TEXT("Steuerung: WASD laufen, Maus umsehen. F = Fliegen an/aus; im Flug Leertaste hoch, C/Q runter, Shift schneller, Mausrad Tempo. K oder Tab = Karte, L = Taschenlampe, E = Fundstück ansehen, N = Notizbuch. Esc = dieses Menü."), TEXT("Controls: WASD to walk, mouse to look around. F = fly on/off; while flying Space up, C/Q down, Shift faster, mouse wheel speed. K or Tab = map, L = flashlight, E = inspect a find, N = notebook. Esc = this menu.")))
					]
					+ SVerticalBox::Slot().AutoHeight().Padding(0, 16, 0, 0).HAlign(HAlign_Right)
					[
						SNew(SButton).OnClicked_Lambda([this] { OnClose.ExecuteIfBound(); return FReply::Handled(); })
						[
							SNew(STextBlock).Font(Font(16)).Text(KdkLoc::T(TEXT("Zurück zum Spiel (Esc)"), TEXT("Back to the game (Esc)")))
						]
					]
				]
			]
		]
	];
}

SKdkSettingsMenu::~SKdkSettingsMenu()
{
	if (ScrollList.IsValid())
	{
		SavedScroll = ScrollList->GetScrollOffset();
	}
}

FReply SKdkSettingsMenu::OnKeyDown(const FGeometry& MyGeometry, const FKeyEvent& InKeyEvent)
{
	if (InKeyEvent.GetKey() == EKeys::Escape || InKeyEvent.GetKey() == EKeys::M)
	{
		OnClose.ExecuteIfBound();
		return FReply::Handled();
	}
	return SCompoundWidget::OnKeyDown(MyGeometry, InKeyEvent);
}

TSharedRef<SWidget> SKdkSettingsMenu::Heading(const FText& Text) const
{
	return SNew(SBox).Padding(FMargin(0, 14, 0, 2))
	[
		SNew(STextBlock).Font(Font(18)).ColorAndOpacity(FLinearColor(0.62f, 0.68f, 0.72f)).Text(Text)
	];
}

TSharedRef<SWidget> SKdkSettingsMenu::CycleRow(const FText& Label, TFunction<FText()> Value, TFunction<void(int32)> Step) const
{
	auto Arrow = [Step](const TCHAR* Glyph, int32 Dir)
	{
		return SNew(SButton).OnClicked_Lambda([Step, Dir] { Step(Dir); return FReply::Handled(); })
			[SNew(STextBlock).Font(Font(15)).Text(FText::FromString(Glyph))];
	};
	return SNew(SHorizontalBox)
		+ SHorizontalBox::Slot().FillWidth(1.f).VAlign(VAlign_Center)[SNew(STextBlock).Font(Font(15)).Text(Label)]
		+ SHorizontalBox::Slot().AutoWidth()[Arrow(TEXT("<"), -1)]
		+ SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center)
		[
			SNew(SBox).WidthOverride(190.f).HAlign(HAlign_Center)
			[SNew(STextBlock).Font(Font(15)).Text_Lambda([Value] { return Value(); })]
		]
		+ SHorizontalBox::Slot().AutoWidth()[Arrow(TEXT(">"), 1)];
}

TSharedRef<SWidget> SKdkSettingsMenu::SliderRow(const FText& Label, TFunction<float()> GetNormalized,
	TFunction<void(float)> SetNormalized, TFunction<FText()> Value) const
{
	return SNew(SHorizontalBox)
		+ SHorizontalBox::Slot().FillWidth(1.f).VAlign(VAlign_Center)[SNew(STextBlock).Font(Font(15)).Text(Label)]
		+ SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center)
		[
			SNew(SBox).WidthOverride(170.f)
			[SNew(SSlider).Value_Lambda([GetNormalized] { return GetNormalized(); }).OnValueChanged_Lambda([SetNormalized](float N) { SetNormalized(N); })]
		]
		+ SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center).Padding(10, 0, 0, 0)
		[
			SNew(SBox).WidthOverride(60.f)[SNew(STextBlock).Font(Font(15)).Text_Lambda([Value] { return Value(); })]
		];
}

#undef LOCTEXT_NAMESPACE
