#include "KdkShooter.h"

#include "Dom/JsonObject.h"
#include "Math/RandomStream.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"

namespace
{
	FVector Metres(const TArray<TSharedPtr<FJsonValue>>& A)
	{
		return A.Num() >= 3 ? FVector(A[0]->AsNumber(), A[1]->AsNumber(), A[2]->AsNumber()) * 100.0 : FVector::ZeroVector;  // [north, east, z] m -> cm
	}

	FVector Metres(const TSharedPtr<FJsonObject>& O, const TCHAR* Field)
	{
		const TArray<TSharedPtr<FJsonValue>>* A;
		return O->TryGetArrayField(Field, A) ? Metres(*A) : FVector::ZeroVector;
	}

	float Num(const TSharedPtr<FJsonObject>& O, const TCHAR* Field, float Default)
	{
		double V;
		return O.IsValid() && O->TryGetNumberField(Field, V) ? float(V) : Default;
	}

	TArray<FVector> Points(const TSharedPtr<FJsonObject>& O, const TCHAR* Field)
	{
		TArray<FVector> Out;
		const TArray<TSharedPtr<FJsonValue>>* A;
		if (O->TryGetArrayField(Field, A))
		{
			for (const TSharedPtr<FJsonValue>& P : *A)
			{
				Out.Add(Metres(P->AsArray()));
			}
		}
		return Out;
	}
}

bool FKdkShooter::Load(const FString& Json)
{
	*this = FKdkShooter();
	TSharedPtr<FJsonObject> Root;
	if (!FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(Json), Root) || !Root.IsValid())
	{
		return false;
	}
	const TSharedPtr<FJsonObject>* Tuning;
	if (Root->TryGetObjectField(TEXT("tuning"), Tuning))
	{
		const TSharedPtr<FJsonObject>* P;
		if ((*Tuning)->TryGetObjectField(TEXT("player"), P))
		{
			Player.Health = Num(*P, TEXT("health"), Player.Health);
			Player.Mag = int32(Num(*P, TEXT("mag"), Player.Mag));
			Player.Reserve = int32(Num(*P, TEXT("reserve"), Player.Reserve));
			Player.Damage = Num(*P, TEXT("damage"), Player.Damage);
			Player.Range = Num(*P, TEXT("range_m"), Player.Range / 100.f) * 100.f;
			Player.Interval = Num(*P, TEXT("interval_s"), Player.Interval);
			Player.Spread = Num(*P, TEXT("spread_deg"), Player.Spread);
			Player.SpreadHip = Num(*P, TEXT("spread_hip_deg"), Player.SpreadHip);
			Player.Reload = Num(*P, TEXT("reload_s"), Player.Reload);
			Player.Fov = Num(*P, TEXT("fov"), Player.Fov);
			Player.FovAim = Num(*P, TEXT("fov_aim"), Player.FovAim);
			Player.Noise = Num(*P, TEXT("noise_m"), Player.Noise / 100.f) * 100.f;
		}
		const TSharedPtr<FJsonObject>* E;
		if ((*Tuning)->TryGetObjectField(TEXT("enemies"), E))
		{
			for (const auto& Pair : (*E)->Values)
			{
				const TSharedPtr<FJsonObject> O = Pair.Value->AsObject();
				FKdkFighter& F = Enemies.FindOrAdd(FString(Pair.Key.ToView()));
				F.Health = Num(O, TEXT("health"), F.Health);
				F.Damage = Num(O, TEXT("damage"), F.Damage);
				F.Interval = Num(O, TEXT("interval_s"), F.Interval);
				F.Burst = FMath::Max(1, int32(Num(O, TEXT("burst"), F.Burst)));
				F.Pause = Num(O, TEXT("pause_s"), F.Pause);
				F.Spread = Num(O, TEXT("spread_deg"), F.Spread);
				F.Range = Num(O, TEXT("range_m"), F.Range / 100.f) * 100.f;
				F.Sight = Num(O, TEXT("sight_m"), F.Sight / 100.f) * 100.f;
				F.React = Num(O, TEXT("react_s"), F.React);
				F.Speed = Num(O, TEXT("speed"), F.Speed);
				F.CoverBelow = Num(O, TEXT("cover_below"), F.CoverBelow);
				F.EngageMin = Num(O, TEXT("engage_min_m"), F.EngageMin / 100.f) * 100.f;
				F.EngageMax = Num(O, TEXT("engage_max_m"), F.EngageMax / 100.f) * 100.f;
				F.Reposition = Num(O, TEXT("reposition_s"), F.Reposition);
			}
		}
		DistortionExponent = Num(*Tuning, TEXT("distortion_exponent"), DistortionExponent);
		ExtractHold = Num(*Tuning, TEXT("extract_hold_s"), ExtractHold);
		TasksPerRound = int32(Num(*Tuning, TEXT("tasks_per_round"), TasksPerRound));
		PickupShare = Num(*Tuning, TEXT("pickup_share"), PickupShare);
		JamTime = Num(*Tuning, TEXT("jam_s"), JamTime);
		Reinforcements = int32(Num(*Tuning, TEXT("reinforcements"), Reinforcements));
		MaxShooters = int32(Num(*Tuning, TEXT("max_shooters"), MaxShooters));
		TargetFps = Num(*Tuning, TEXT("target_fps"), TargetFps);
		SafeStart = Num(*Tuning, TEXT("safe_start_m"), SafeStart / 100.f) * 100.f;
		RegenDelay = Num(*Tuning, TEXT("regen_delay_s"), RegenDelay);
		HealthRegen = Num(*Tuning, TEXT("health_regen"), HealthRegen);
		VisionRegen = Num(*Tuning, TEXT("vision_regen"), VisionRegen);
	}
	const TSharedPtr<FJsonObject>* ItemsObj;
	if (Root->TryGetObjectField(TEXT("items"), ItemsObj))
	{
		for (const auto& Pair : (*ItemsObj)->Values)
		{
			const TSharedPtr<FJsonObject> O = Pair.Value->AsObject();
			FKdkItem& I = Items.FindOrAdd(FString(Pair.Key.ToView()));
			I.Heal = Num(O, TEXT("heal"), 0.f);
			I.Armor = Num(O, TEXT("armor"), 0.f);
			I.Rounds = int32(Num(O, TEXT("rounds"), 0.f));
		}
	}
	const TArray<TSharedPtr<FJsonValue>>* A;
	if (Root->TryGetArrayField(TEXT("flats"), A))
	{
		for (const TSharedPtr<FJsonValue>& V : *A)
		{
			const TSharedPtr<FJsonObject> O = V->AsObject();
			FKdkFlat& F = Flats.AddDefaulted_GetRef();
			F.Where = O->GetStringField(TEXT("where"));
			O->TryGetStringField(TEXT("where_en"), F.WhereEn);
			F.Item = O->GetStringField(TEXT("item"));
			F.Points = Points(O, TEXT("points"));
			if (F.Points.IsEmpty())
			{
				Flats.Pop();
			}
		}
	}
	if (Root->TryGetArrayField(TEXT("tasks"), A))
	{
		for (const TSharedPtr<FJsonValue>& V : *A)
		{
			const TSharedPtr<FJsonObject> O = V->AsObject();
			FKdkTask& T = TaskPool.AddDefaulted_GetRef();
			T.Id = O->GetStringField(TEXT("id"));
			T.Kind = O->GetStringField(TEXT("kind"));
			O->TryGetStringField(TEXT("item"), T.Item);
			O->TryGetStringField(TEXT("mesh"), T.Mesh);
			T.Goal = O->GetStringField(TEXT("goal"));
			O->TryGetStringField(TEXT("goal_en"), T.GoalEn);
			T.Done = O->GetStringField(TEXT("done"));
			O->TryGetStringField(TEXT("done_en"), T.DoneEn);
			T.Pos = Metres(O, TEXT("pos"));
		}
	}
	if (Root->TryGetArrayField(TEXT("starts"), A))
	{
		for (const TSharedPtr<FJsonValue>& V : *A)
		{
			const TArray<TSharedPtr<FJsonValue>>& S = V->AsArray();
			if (S.Num() >= 4)
			{
				Starts.Add({FString(), Metres(S), float(S[3]->AsNumber())});
			}
		}
	}
	if (Root->TryGetArrayField(TEXT("patrols"), A))
	{
		for (const TSharedPtr<FJsonValue>& V : *A)
		{
			Patrols.Add(Points(V->AsObject(), TEXT("route")));
		}
	}
	Turrets = Points(Root, TEXT("turrets"));
	Drones = Points(Root, TEXT("drones"));
	if (Root->TryGetArrayField(TEXT("obstacles"), A))
	{
		for (const TSharedPtr<FJsonValue>& V : *A)
		{
			const TSharedPtr<FJsonObject> O = V->AsObject();
			Obstacles.Add({O->GetStringField(TEXT("mesh")), Metres(O, TEXT("pos")), Num(O, TEXT("yaw"), 0.f)});
		}
	}
	PowerSwitch = Metres(Root, TEXT("power_switch"));
	const TSharedPtr<FJsonObject>* AreaObj;
	if (Root->TryGetObjectField(TEXT("area"), AreaObj))
	{
		auto Range = [&](const TCHAR* Field) -> FVector2D
		{
			const TArray<TSharedPtr<FJsonValue>>* R;
			return (*AreaObj)->TryGetArrayField(Field, R) && R->Num() == 2 ? FVector2D((*R)[0]->AsNumber(), (*R)[1]->AsNumber()) * 100.0 : FVector2D::ZeroVector;
		};
		const FVector2D N = Range(TEXT("north")), E = Range(TEXT("east")), Z = Range(TEXT("z"));
		Area = FBox(FVector(N.X, E.X, Z.X), FVector(N.Y, E.Y, Z.Y));
	}
	return Starts.Num() >= 2 && TaskPool.Num() > 0 && Flats.Num() > 0;
}

void FKdkShooter::BeginRound(int32 Seed)
{
	FRandomStream Rand(Seed);
	Health = Vision = Player.Health;
	SinceHit = 0.f;
	Armor = 0.f;
	Mag = Player.Mag;
	Reserve = Player.Reserve;
	Current = 0;

	TArray<int32> Order;
	for (int32 I = 0; I < TaskPool.Num(); ++I)
	{
		Order.Insert(I, Rand.RandRange(0, Order.Num()));
	}
	Tasks.Reset();
	for (int32 I = 0; I < FMath::Min(TasksPerRound, Order.Num()); ++I)
	{
		Tasks.Add(TaskPool[Order[I]]);
	}
	// the radio lies in a random flat; its point is kept free of the household's own pickup
	int32 RadioFlat = INDEX_NONE, RadioPoint = INDEX_NONE;
	for (FKdkTask& T : Tasks)
	{
		if (T.Kind == TEXT("fetch_flat"))
		{
			RadioFlat = Rand.RandRange(0, Flats.Num() - 1);
			RadioPoint = Rand.RandRange(0, Flats[RadioFlat].Points.Num() - 1);
			T.Pos = Flats[RadioFlat].Points[RadioPoint];
			const FKdkFlat& F = Flats[RadioFlat];
			T.Goal = T.Goal.Replace(TEXT("{where}"), *F.Where);
			T.GoalEn = T.GoalEn.Replace(TEXT("{where}"), *(F.WhereEn.IsEmpty() ? F.Where : F.WhereEn));
		}
	}
	Pickups.Reset();
	for (int32 F = 0; F < Flats.Num(); ++F)
	{
		if (Rand.FRand() >= PickupShare)
		{
			continue;
		}
		int32 P = Rand.RandRange(0, Flats[F].Points.Num() - 1);
		if (F == RadioFlat && P == RadioPoint)
		{
			if (Flats[F].Points.Num() == 1)
			{
				continue;  // one spot only: the radio has it
			}
			P = (P + 1) % Flats[F].Points.Num();
		}
		Pickups.Add({Flats[F].Item, Flats[F].Points[P], F, false});
	}
	Start = Rand.RandRange(0, Starts.Num() - 1);
	Extract = Start;
	for (int32 I = 0; I < Starts.Num(); ++I)
	{
		if (FVector::DistSquared2D(Starts[I].Pos, Starts[Start].Pos) > FVector::DistSquared2D(Starts[Extract].Pos, Starts[Start].Pos))
		{
			Extract = I;
		}
	}
}

float FKdkShooter::Hit(float Damage)
{
	const float Absorbed = FMath::Min(Armor, Damage * 0.6f);
	Armor -= Absorbed;
	Health = FMath::Max(0.f, Health - (Damage - Absorbed));
	Vision = Health;
	SinceHit = 0.f;
	return Health;
}

void FKdkShooter::Recover(float DeltaSeconds)
{
	SinceHit += DeltaSeconds;
	if (IsDown() || SinceHit < RegenDelay)
	{
		return;
	}
	Health = FMath::Min(Player.Health, Health + HealthRegen * DeltaSeconds);
	Vision = FMath::Clamp(Vision + VisionRegen * DeltaSeconds, Health, Player.Health);
}

float FKdkShooter::Distortion() const
{
	const float Lost = 1.f - FMath::Clamp(Vision / FMath::Max(1.f, Player.Health), 0.f, 1.f);
	return FMath::Pow(Lost, DistortionExponent);
}

bool FKdkShooter::Take(int32 Pickup)
{
	if (!Pickups.IsValidIndex(Pickup) || Pickups[Pickup].bTaken)
	{
		return false;
	}
	const FKdkItem* I = Items.Find(Pickups[Pickup].Item);
	if (!I || (I->Heal > 0.f && Health >= Player.Health))
	{
		return false;
	}
	Health = FMath::Min(Player.Health, Health + I->Heal);
	Vision = FMath::Max(Vision, Health);
	Armor += I->Armor;
	Reserve += I->Rounds;
	Pickups[Pickup].bTaken = true;
	return true;
}

bool FKdkShooter::Shoot()
{
	if (Mag <= 0)
	{
		return false;
	}
	--Mag;
	return true;
}

void FKdkShooter::Reload()
{
	const int32 Moved = FMath::Min(Player.Mag - Mag, Reserve);
	Mag += Moved;
	Reserve -= Moved;
}

bool FKdkShooter::CompleteTask()
{
	if (!Tasks.IsValidIndex(Current))
	{
		return false;
	}
	Tasks[Current++].bDone = true;
	return AllTasksDone();
}
