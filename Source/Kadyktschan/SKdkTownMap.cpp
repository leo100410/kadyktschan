#include "SKdkTownMap.h"

#include "Brushes/SlateRoundedBoxBrush.h"
#include "Dom/JsonObject.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Rendering/DrawElements.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"
#include "Styling/CoreStyle.h"
#include "KdkLoc.h"
#include "InputCoreTypes.h"
#include "Layout/Clipping.h"

namespace
{
	// survey-sheet palette, kept dark so the map does not flash in a dark interior
	const FLinearColor Paper(0.035f, 0.038f, 0.035f, 1.f);
	const FLinearColor Building(0.20f, 0.205f, 0.19f);
	const FLinearColor Road(0.11f, 0.115f, 0.105f);
	const FLinearColor River(0.16f, 0.30f, 0.40f);
	const FLinearColor Story(0.85f, 0.25f, 0.18f);
	const FLinearColor Base(0.35f, 0.58f, 0.80f);
	const FLinearColor Ink(0.88f, 0.87f, 0.82f);
	const FLinearColor Muted(0.55f, 0.56f, 0.52f);

	FVector2f ReadPoint(const TSharedPtr<FJsonValue>& V)
	{
		const TArray<TSharedPtr<FJsonValue>>& A = V->AsArray();
		return A.Num() >= 2 ? FVector2f(A[0]->AsNumber(), A[1]->AsNumber()) : FVector2f::ZeroVector;
	}

	void ReadLines(const TSharedPtr<FJsonObject>& Root, const TCHAR* Field, TArray<TArray<FVector2f>>& Out)
	{
		const TArray<TSharedPtr<FJsonValue>>* Lines;
		if (!Root->TryGetArrayField(Field, Lines)) { return; }
		for (const TSharedPtr<FJsonValue>& L : *Lines)
		{
			TArray<FVector2f>& Pts = Out.AddDefaulted_GetRef();
			for (const TSharedPtr<FJsonValue>& P : L->AsArray()) { Pts.Add(ReadPoint(P)); }
		}
	}
}

bool SKdkTownMap::LoadPlan(const FString& Json, FKdkTownPlan& Out)
{
	Out = FKdkTownPlan();
	TSharedPtr<FJsonObject> Root;
	if (!FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(Json), Root) || !Root.IsValid()) { return false; }
	const TArray<TSharedPtr<FJsonValue>>* Items;
	if (!Root->TryGetArrayField(TEXT("buildings"), Items)) { return false; }
	for (const TSharedPtr<FJsonValue>& V : *Items)
	{
		const TArray<TSharedPtr<FJsonValue>>& A = V->AsArray();
		if (A.Num() < 5) { continue; }
		FKdkTownPlan::FBuilding B{FVector2f(A[0]->AsNumber(), A[1]->AsNumber()), (float)A[2]->AsNumber(), (float)A[3]->AsNumber(), (float)A[4]->AsNumber()};
		Out.Buildings.Add(B);
		Out.Bounds += B.Centre;
	}
	ReadLines(Root, TEXT("roads"), Out.Roads);
	ReadLines(Root, TEXT("rivers"), Out.Rivers);
	if (Root->TryGetArrayField(TEXT("places"), Items))
	{
		for (const TSharedPtr<FJsonValue>& V : *Items)
		{
			const TSharedPtr<FJsonObject>& O = V->AsObject();
			FKdkTownPlace& P = Out.Places.AddDefaulted_GetRef();
			P.Name = O->GetStringField(TEXT("name"));
			O->TryGetStringField(TEXT("name_en"), P.NameEn);
			P.bStory = O->GetStringField(TEXT("kind")) == TEXT("story");
			P.Pos = FVector2f(O->GetNumberField(TEXT("east_m")), O->GetNumberField(TEXT("north_m")));
			P.Entry = P.Pos;
			const TArray<TSharedPtr<FJsonValue>>* Entry;
			if (O->TryGetArrayField(TEXT("entry"), Entry) && Entry->Num() >= 2)
			{
				P.Entry = FVector2f((*Entry)[0]->AsNumber(), (*Entry)[1]->AsNumber());
			}
			O->TryGetNumberField(TEXT("floors"), P.Floors);
			O->TryGetStringField(TEXT("details"), P.Details);
			O->TryGetStringField(TEXT("details_en"), P.DetailsEn);
			Out.Bounds += P.Pos;  // places outside the town (Stollen 3) widen the sheet
		}
	}
	Out.Bounds = Out.Bounds.ExpandBy(60.f);  // room for the outermost footprints and labels
	return Out.Buildings.Num() > 0;
}

void SKdkTownMap::Construct(const FArguments& InArgs)
{
	PlayerView = InArgs._PlayerView;
	bDetailed = InArgs._Detailed;
	OnClose = InArgs._OnClose;
	SetClipping(EWidgetClipping::ClipToBounds);  // roads run on past the town; keep them inside the sheet
	Plan = MakeShared<FKdkTownPlan>();
	FString Json;
	const FString Path = FPaths::ProjectContentDir() / TEXT("Kadykchan/Data/TownMap.json");
	if (!FFileHelper::LoadFileToString(Json, *Path) || !LoadPlan(Json, *Plan))
	{
		UE_LOG(LogTemp, Warning, TEXT("Town map: could not read %s"), *Path);
	}
}

TArray<FVector2f> SKdkTownMap::LayoutMarkers(const TArray<FVector2f>& Anchors, const FBox2f& Area)
{
	TArray<FVector2f> Markers;
	for (const FVector2f& Anchor : Anchors)
	{
		FVector2f Candidate = Anchor;
		bool bPlaced = false;
		for (int32 Ring=0; Ring<=20 && !bPlaced; ++Ring)
		{
			for (int32 J=0; J<(Ring ? 16 : 1); ++J)
			{
				const float Angle = J * 2.f * PI / 16.f;
				Candidate = Anchor + FVector2f(FMath::Cos(Angle), FMath::Sin(Angle)) * (Ring * 26.f);
				Candidate.X = FMath::Clamp(Candidate.X, Area.Min.X, Area.Max.X);
				Candidate.Y = FMath::Clamp(Candidate.Y, Area.Min.Y, Area.Max.Y);
				if (!Markers.ContainsByPredicate([&](const FVector2f& Other) { return (Other-Candidate).SizeSquared() < 26.f*26.f; }))
				{
					bPlaced = true;
					break;
				}
			}
		}
		Markers.Add(Candidate);
	}
	return Markers;
}

FReply SKdkTownMap::OnMouseButtonDown(const FGeometry& Geometry, const FPointerEvent& Event)
{
	return bDetailed ? FReply::Handled().SetUserFocus(SharedThis(this),EFocusCause::Mouse) : FReply::Unhandled();
}

FReply SKdkTownMap::OnKeyDown(const FGeometry& Geometry, const FKeyEvent& Event)
{
	if (bDetailed && (Event.GetKey()==EKeys::Escape || Event.GetKey()==EKeys::M || Event.GetKey()==EKeys::K || Event.GetKey()==EKeys::Tab))
	{
		OnClose.ExecuteIfBound();
		return FReply::Handled();
	}
	return FReply::Unhandled();
}

int32 SKdkTownMap::OnPaint(const FPaintArgs& Args, const FGeometry& G, const FSlateRect& MyCullingRect,
	FSlateWindowElementList& Out, int32 LayerId, const FWidgetStyle& InWidgetStyle, bool bParentEnabled) const
{
	static const FSlateRoundedBoxBrush Disc(FLinearColor::White, 11.f);
	const FSlateBrush* White = FCoreStyle::Get().GetBrush("WhiteBrush");
	const FVector2f Size = G.GetLocalSize();
	FSlateDrawElement::MakeBox(Out, LayerId, G.ToPaintGeometry(), White, ESlateDrawEffect::None, Paper);
	const FSlateFontInfo Title = FCoreStyle::GetDefaultFontStyle("Bold", 21);
	const FSlateFontInfo Label = FCoreStyle::GetDefaultFontStyle("Regular", 12);
	const FSlateFontInfo Small = FCoreStyle::GetDefaultFontStyle("Regular", 10);
	auto Text = [&](const FString& S, FVector2f At, const FSlateFontInfo& Font, const FLinearColor& C, int32 Layer)
	{
		FSlateDrawElement::MakeText(Out, Layer, G.ToPaintGeometry(FVector2f(600.f,40.f),FSlateLayoutTransform(At)),S,Font,ESlateDrawEffect::None,C);
	};
	Text(bDetailed ? KdkLoc::S(TEXT("Eingerichtete Häuser und Etagen"),TEXT("Furnished houses and floors")) : KdkLoc::S(TEXT("Karte von Kadyktschan"),TEXT("Map of Kadykchan")),FVector2f(24,20),Title,Ink,LayerId+5);
	Text(bDetailed ? KdkLoc::S(TEXT("Nummern: offene Eingänge · Etagenliste: links / rechts. Esc: zurück."),TEXT("Numbers: open entrances · floor list: left / right. Esc: back.")) : KdkLoc::S(TEXT("K / Tab: schließen · Namen rechts nach Nummer"),TEXT("K / Tab: close · names listed by number on the right")),FVector2f(24,53),Label,Muted,LayerId+5);
	if (!Plan.IsValid() || Plan->Buildings.IsEmpty()) return LayerId+5;
	TArray<int32> Visible;
	FBox2f Bounds = Plan->Bounds;
	if (bDetailed) Bounds = FBox2f(ForceInit);
	for (int32 I=0; I<Plan->Places.Num(); ++I)
	{
		const FKdkTownPlace& P = Plan->Places[I];
		if (bDetailed && P.Floors<2) continue;
		Visible.Add(I);
		if (bDetailed) { Bounds += P.Pos; Bounds += P.Entry; }
	}
	if (Visible.IsEmpty())
	{
		Text(KdkLoc::S(TEXT("Keine eingerichteten Etagen in den Kartendaten."),TEXT("No furnished floors in map data.")),FVector2f(24,100),Label,Ink,LayerId+5);
		return LayerId+5;
	}
	if (bDetailed) Bounds=Bounds.ExpandBy(70.f);
	const float Sidebar = FMath::Min(350.f, Size.X*.38f);
	const FVector2f Area0(24,84),AreaSize(FMath::Max(80.f,Size.X-Sidebar-72.f),FMath::Max(80.f,Size.Y-130.f));
	const FVector2f Span = Bounds.GetSize();
	const float Scale=FMath::Min(AreaSize.X/FMath::Max(1.f,Span.X),AreaSize.Y/FMath::Max(1.f,Span.Y));
	const FVector2f Origin=Area0+(AreaSize-Span*Scale)*.5f;
	auto Screen=[&](FVector2f P) { return Origin+FVector2f(P.X-Bounds.Min.X,Bounds.Max.Y-P.Y)*Scale; };
	Out.PushClip(FSlateClippingZone(G.ToPaintGeometry(AreaSize,FSlateLayoutTransform(Area0))));
	for (const auto& Line : Plan->Rivers)
	{
		TArray<FVector2f> Points; for (const auto& P : Line) Points.Add(Screen(P));
		if (Points.Num()>1) FSlateDrawElement::MakeLines(Out,LayerId+1,G.ToPaintGeometry(),Points,ESlateDrawEffect::None,River,true,FMath::Max(2.f,7.f*Scale));
	}
	for (const auto& Line : Plan->Roads)
	{
		TArray<FVector2f> Points; for (const auto& P : Line) Points.Add(Screen(P));
		if (Points.Num()>1) FSlateDrawElement::MakeLines(Out,LayerId+1,G.ToPaintGeometry(),Points,ESlateDrawEffect::None,Road,true,FMath::Max(2.f,6.f*Scale));
	}
	for (const auto& B : Plan->Buildings)
	{
		const auto* Place=Plan->Places.FindByPredicate([&](const FKdkTownPlace& P) { return P.Pos.Equals(B.Centre,.5f); });
		const FVector2f Box(B.Length*Scale,B.Width*Scale);
		FSlateDrawElement::MakeBox(Out,LayerId+2,G.ToPaintGeometry(Box,FSlateLayoutTransform(Screen(B.Centre)-Box*.5f),FSlateRenderTransform(FQuat2f(FMath::DegreesToRadians(-B.AxisDeg)))),White,ESlateDrawEffect::None,Place ? (Place->bStory ? Story : Base) : Building);
	}
	TArray<FVector2f> Anchors;
	for (int32 I : Visible) Anchors.Add(Screen(bDetailed ? Plan->Places[I].Entry : Plan->Places[I].Pos));
	const auto Markers=LayoutMarkers(Anchors,FBox2f(Area0+FVector2f(12,12),Area0+AreaSize-FVector2f(12,12)));
	for (int32 J=0; J<Visible.Num(); ++J)
	{
		const int32 I=Visible[J];const auto& P=Plan->Places[I];const auto C=Markers[J];
		const FLinearColor Color=P.bStory ? Story : Base;
		FSlateDrawElement::MakeLines(Out,LayerId+3,G.ToPaintGeometry(),TArray<FVector2f>{Anchors[J],C},ESlateDrawEffect::None,Ink,true,1.f);
		FSlateDrawElement::MakeBox(Out,LayerId+3,G.ToPaintGeometry(FVector2f(5,5),FSlateLayoutTransform(Anchors[J]-FVector2f(2.5f,2.5f))),White,ESlateDrawEffect::None,Ink);
		FSlateDrawElement::MakeBox(Out,LayerId+4,G.ToPaintGeometry(FVector2f(22,22),FSlateLayoutTransform(C-FVector2f(11,11))),&Disc,ESlateDrawEffect::None,Color);
		Text(FString::FromInt(I+1),C-FVector2f(I>=9 ? 6.f : 3.f,7.f),Small,Paper,LayerId+5);
	}
	if (PlayerView)
	{
		const FVector3f V=PlayerView();const auto C=Screen(FVector2f(V.X,V.Y));
		const float A=FMath::DegreesToRadians(V.Z);const FVector2f D(FMath::Sin(A),-FMath::Cos(A)),R(D.Y,-D.X);
		FSlateDrawElement::MakeLines(Out,LayerId+6,G.ToPaintGeometry(),TArray<FVector2f>{C+D*12.f,C-D*7.f+R*6.f,C-D*4.f,C-D*7.f-R*6.f,C+D*12.f},ESlateDrawEffect::None,FLinearColor(1,.95,.6),true,2.f);
		Text(KdkLoc::S(TEXT("Du"),TEXT("You")),C+FVector2f(14,4),Small,Ink,LayerId+6);
	}
	Out.PopClip();
	const FVector2f List0(Size.X-Sidebar,84);
	const float Row=FMath::Min(bDetailed ? 110.f : 34.f,AreaSize.Y/Visible.Num());
	for (int32 J=0; J<Visible.Num(); ++J)
	{
		const int32 I=Visible[J];const auto& P=Plan->Places[I];const auto C=List0+FVector2f(0,J*Row);
		Text(FString::Printf(TEXT("%d  %s"),I+1,*KdkLoc::S(P.Name,P.NameEn)),C,Label,P.bStory ? Story : Base,LayerId+5);
		if (bDetailed)
		{
			TArray<FString> Lines; KdkLoc::S(P.Details,P.DetailsEn).ParseIntoArrayLines(Lines);
			for (int32 K=0; K<Lines.Num(); ++K) Text(Lines[K],C+FVector2f(0,20+K*15),Small,Ink,LayerId+5);
		}
	}
	const FVector2f S0(24,Size.Y-26);
	FSlateDrawElement::MakeLines(Out,LayerId+5,G.ToPaintGeometry(),TArray<FVector2f>{S0,S0+FVector2f(100*Scale,0)},ESlateDrawEffect::None,Muted,true,2.f);
	Text(TEXT("100 m"),S0+FVector2f(100*Scale+8,-7),Small,Muted,LayerId+5);
	return LayerId+6;
}
