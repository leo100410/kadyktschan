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

#define LOCTEXT_NAMESPACE "KdkSettings"

namespace
{
	FSlateFontInfo Font(int32 Size) { return FCoreStyle::GetDefaultFontStyle("Regular", Size); }

	FText QualityText(int32 Level)
	{
		switch (Level)
		{
		case 0: return LOCTEXT("Low", "Niedrig");
		case 1: return LOCTEXT("Medium", "Mittel");
		case 2: return LOCTEXT("High", "Hoch");
		case 3: return LOCTEXT("Epic", "Episch");
		case 4: return LOCTEXT("Cinematic", "Kino");
		default: return LOCTEXT("Custom", "Benutzerdefiniert");
		}
	}

	FText OnOff(bool b) { return b ? LOCTEXT("On", "An") : LOCTEXT("Off", "Aus"); }

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
		{ LOCTEXT("ViewDistance", "Sichtweite"), &UGameUserSettings::GetViewDistanceQuality, &UGameUserSettings::SetViewDistanceQuality },
		{ LOCTEXT("Shadows", "Schatten"), &UGameUserSettings::GetShadowQuality, &UGameUserSettings::SetShadowQuality },
		{ LOCTEXT("GI", "Globale Beleuchtung"), &UGameUserSettings::GetGlobalIlluminationQuality, &UGameUserSettings::SetGlobalIlluminationQuality },
		{ LOCTEXT("Reflections", "Reflexionen"), &UGameUserSettings::GetReflectionQuality, &UGameUserSettings::SetReflectionQuality },
		{ LOCTEXT("Textures", "Texturen"), &UGameUserSettings::GetTextureQuality, &UGameUserSettings::SetTextureQuality },
		{ LOCTEXT("Effects", "Effekte"), &UGameUserSettings::GetVisualEffectQuality, &UGameUserSettings::SetVisualEffectQuality },
		{ LOCTEXT("Foliage", "Vegetation"), &UGameUserSettings::GetFoliageQuality, &UGameUserSettings::SetFoliageQuality },
		{ LOCTEXT("PostProcess", "Nachbearbeitung"), &UGameUserSettings::GetPostProcessingQuality, &UGameUserSettings::SetPostProcessingQuality },
		{ LOCTEXT("AA", "Kantenglättung"), &UGameUserSettings::GetAntiAliasingQuality, &UGameUserSettings::SetAntiAliasingQuality },
		{ LOCTEXT("Shading", "Materialqualität"), &UGameUserSettings::GetShadingQuality, &UGameUserSettings::SetShadingQuality },
	};

	TSharedRef<SScrollBox> List = SNew(SScrollBox);
	ScrollList = List;
	auto Add = [&List](TSharedRef<SWidget> W) { List->AddSlot().Padding(0, 3)[W]; };

	Add(Heading(LOCTEXT("Mouse", "Maus")));
	Add(SliderRow(LOCTEXT("Sensitivity", "Empfindlichkeit"),
		[S] { return (S->MouseSensitivity - 0.1f) / 2.9f; },
		[S](float N) { S->MouseSensitivity = FMath::RoundToFloat((0.1f + N * 2.9f) * 20.f) / 20.f; },
		[S] { return FText::AsNumber(S->MouseSensitivity); }));
	Add(CycleRow(LOCTEXT("InvertY", "Maus-Y umkehren"), [S] { return OnOff(S->bInvertMouseY); },
		[S](int32) { S->bInvertMouseY = !S->bInvertMouseY; }));

	Add(Heading(LOCTEXT("Graphics", "Grafik")));
	Add(CycleRow(LOCTEXT("Preset", "Gesamtqualität"), [S] { return QualityText(S->GetOverallScalabilityLevel()); },
		[S](int32 Dir) { S->SetOverallScalabilityLevel(StepQuality(FMath::Max(S->GetOverallScalabilityLevel(), 1), Dir)); Apply(S); }));
	Add(SliderRow(LOCTEXT("ResScale", "Renderauflösung"),
		[S] { float N, V, Min, Max; S->GetResolutionScaleInformationEx(N, V, Min, Max);
			return FMath::Clamp((V - UKdkGameUserSettings::MinRenderScale) / (100.f - UKdkGameUserSettings::MinRenderScale), 0.f, 1.f); },
		[S](float N) { S->SetResolutionScaleValueEx(FMath::RoundToFloat(FMath::Lerp(UKdkGameUserSettings::MinRenderScale, 100.f, N) / 5.f) * 5.f); Apply(S); },
		[S] { float N, V, Min, Max; S->GetResolutionScaleInformationEx(N, V, Min, Max); return FText::Format(LOCTEXT("Pct", "{0} %"), FText::AsNumber(FMath::RoundToInt(V))); }));
	for (const FGroup& G : Groups)
	{
		Add(CycleRow(G.Label, [S, G] { return QualityText((S->*G.Get)()); },
			[S, G](int32 Dir) { (S->*G.Set)(StepQuality((S->*G.Get)(), Dir)); Apply(S); }));
	}
	Add(CycleRow(LOCTEXT("RT", "Raytracing (Hardware)"), [S] { return OnOff(S->bHardwareRayTracing); },
		[S](int32) { S->bHardwareRayTracing = !S->bHardwareRayTracing; Apply(S); }));
	Add(CycleRow(LOCTEXT("Nanite", "Nanite"), [S] { return OnOff(S->bNanite); },
		[S](int32) { S->bNanite = !S->bNanite; Apply(S); }));

	Add(Heading(LOCTEXT("Display", "Anzeige")));
	Add(CycleRow(LOCTEXT("WindowMode", "Fenstermodus"),
		[S]
		{
			switch (S->GetFullscreenMode())
			{
			case EWindowMode::Fullscreen: return LOCTEXT("Fullscreen", "Vollbild");
			case EWindowMode::WindowedFullscreen: return LOCTEXT("Borderless", "Vollbild (Fenster)");
			default: return LOCTEXT("Windowed", "Fenster");
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
	Add(CycleRow(LOCTEXT("VSync", "VSync"), [S] { return OnOff(S->IsVSyncEnabled()); },
		[S](int32) { S->SetVSyncEnabled(!S->IsVSyncEnabled()); Apply(S); }));
	Add(CycleRow(LOCTEXT("FrameLimit", "Bildrate-Limit"),
		[S] { const float L = S->GetFrameRateLimit(); return L <= 0.f ? LOCTEXT("Unlimited", "Unbegrenzt") : FText::AsNumber(FMath::RoundToInt(L)); },
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
	Add(CycleRow(LOCTEXT("Camcorder", "Videokamera"), [S] { return OnOff(S->bCamcorder); },
		[S](int32) { S->bCamcorder = !S->bCamcorder; }));  // applied by the player controller
	Add(SliderRow(LOCTEXT("Brightness", "Helligkeit"), [S] { return (S->Brightness + 2.f) / 4.f; },
		[S](float N) { S->Brightness = FMath::RoundToFloat((N * 4.f - 2.f) * 10.f) / 10.f; },
		[S] { return FText::AsNumber(S->Brightness); }));
	Add(SliderRow(LOCTEXT("DuskAmount", "Dämmerungsstärke"), [S] { return S->DuskAmount; },
		[S](float N) { S->DuskAmount = FMath::RoundToFloat(N * 20.f) / 20.f; },
		[S] { return FText::Format(LOCTEXT("PctD", "{0} %"), FText::AsNumber(FMath::RoundToInt(S->DuskAmount * 100))); }));
	Add(SliderRow(LOCTEXT("CamPixel", "Verpixelung (Videokamera)"), [S] { return S->CamPixelation; },
		[S](float N) { S->CamPixelation = FMath::RoundToFloat(N * 20.f) / 20.f; },
		[S] { return FText::Format(LOCTEXT("PctP", "{0} %"), FText::AsNumber(FMath::RoundToInt(S->CamPixelation * 100))); }));
	Add(SliderRow(LOCTEXT("CamNoise", "Stärke (Videokamera)"), [S] { return S->CamNoise; },
		[S](float N) { S->CamNoise = FMath::RoundToFloat(N * 20.f) / 20.f; },
		[S] { return FText::Format(LOCTEXT("PctN", "{0} %"), FText::AsNumber(FMath::RoundToInt(S->CamNoise * 100))); }));
	Add(SliderRow(LOCTEXT("Fog", "Nebel"), [S] { return S->FogAmount / 3.f; },
		[S](float N) { S->FogAmount = FMath::RoundToFloat(N * 30.f) / 10.f; },
		[S] { return FText::Format(LOCTEXT("PctF", "{0} %"), FText::AsNumber(FMath::RoundToInt(S->FogAmount * 100))); }));
	Add(CycleRow(LOCTEXT("Dusk", "Dämmerung"), [S] { return OnOff(S->bDusk); },
		[S](int32) { S->bDusk = !S->bDusk; }));  // the sky cycle actor reads it on its next tick
	Add(CycleRow(LOCTEXT("ShowFPS", "Bilder pro Sekunde anzeigen"), [S] { return OnOff(S->bShowFPS); },
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
						SNew(STextBlock).Font(Font(26)).Text(LOCTEXT("Title", "Einstellungen"))
					]
					+ SVerticalBox::Slot().FillHeight(1.f)
					[
						List
					]
					+ SVerticalBox::Slot().AutoHeight().Padding(0, 12, 0, 0)
					[
						SNew(STextBlock).Font(Font(13)).ColorAndOpacity(FLinearColor(0.62f, 0.68f, 0.72f)).AutoWrapText(true)
						.Text(LOCTEXT("Controls", "Steuerung: WASD laufen, Maus umsehen. F = Fliegen an/aus; im Flug Leertaste/E hoch, C/Q runter, Shift schneller, Mausrad Tempo. Esc = dieses Menü."))
					]
					+ SVerticalBox::Slot().AutoHeight().Padding(0, 16, 0, 0).HAlign(HAlign_Right)
					[
						SNew(SButton).OnClicked_Lambda([this] { OnClose.ExecuteIfBound(); return FReply::Handled(); })
						[
							SNew(STextBlock).Font(Font(16)).Text(LOCTEXT("Back", "Zurück zum Spiel (Esc)"))
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
