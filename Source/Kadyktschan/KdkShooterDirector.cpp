#include "KdkShooterDirector.h"

#include "Components/BrushComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/DamageEvents.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kadyktschan.h"
#include "KadyktschanCharacter.h"
#include "KadyktschanPlayerController.h"
#include "KdkEnemy.h"
#include "KdkLoc.h"
#include "KdkStory.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/CommandLine.h"
#include "Misc/FileHelper.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "NavigationPath.h"
#include "NavigationSystem.h"
#include "NavMesh/NavMeshBoundsVolume.h"
#include "PhysicsEngine/BodySetup.h"
#include "Sound/SoundAttenuation.h"
#include "Sound/SoundBase.h"

namespace
{
	template <typename T>
	T* Load(const FString& Folder, const FString& Name)
	{
		return LoadObject<T>(nullptr, *FString::Printf(TEXT("/Game/Kadykchan/Shooter/%s%s.%s"), *Folder, *Name, *Name));
	}

	FString ItemMesh(const FString& Item)
	{
		return TEXT("SM_Shooter_") + Item.Left(1).ToUpper() + Item.Mid(1);  // bandage -> SM_Shooter_Bandage
	}

	FString ItemName(const FString& Item)
	{
		if (Item == TEXT("bandage")) return KdkLoc::S(TEXT("Verbandszeug"), TEXT("Bandages"));
		if (Item == TEXT("medkit")) return KdkLoc::S(TEXT("Verbandskasten"), TEXT("First-aid kit"));
		if (Item == TEXT("ammo")) return KdkLoc::S(TEXT("Munitionskiste"), TEXT("Ammunition box"));
		if (Item == TEXT("vest")) return KdkLoc::S(TEXT("Schutzweste"), TEXT("Protective vest"));
		return Item;
	}

	FString FormatTime(float Seconds)
	{
		const int32 S = FMath::Max(0, FMath::RoundToInt(Seconds));
		return FString::Printf(TEXT("%d:%02d"), S / 60, S % 60);
	}
}

AKdkShooterDirector::AKdkShooterDirector()
{
	PrimaryActorTick.bCanEverTick = true;
	RootComponent = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
}

APawn* AKdkShooterDirector::PlayerPawn() const
{
	return Player.IsValid() ? Player->GetPawn() : nullptr;
}

bool AKdkShooterDirector::IsJammed() const
{
	return Clock < JamUntil;
}

FVector AKdkShooterDirector::Ground(const FVector& Pos, float Up) const
{
	FHitResult Hit;
	FCollisionQueryParams Params(SCENE_QUERY_STAT(KdkShooterGround), true, this);
	Params.AddIgnoredActor(PlayerPawn());
	return GetWorld()->LineTraceSingleByChannel(Hit, Pos + FVector(0.f, 0.f, Up), Pos - FVector(0.f, 0.f, 600.f), ECC_Visibility, Params)
		? Hit.ImpactPoint : Pos;
}

UStaticMeshComponent* AKdkShooterDirector::Place(const FString& Name, const FVector& Pos, float Yaw, float Up, float Scale)
{
	UStaticMesh* Mesh = Load<UStaticMesh>(FString(), Name);
	if (!Mesh)
	{
		UE_LOG(LogKadyktschan, Warning, TEXT("Shooter mesh %s missing: run tools/rebuild_shooter.sh"), *Name);
		return nullptr;
	}
	// runtime components of this actor, not level actors: the story map is never changed
	UStaticMeshComponent* C = NewObject<UStaticMeshComponent>(this);
	C->SetMobility(EComponentMobility::Movable);
	C->SetStaticMesh(Mesh);
	C->SetWorldLocationAndRotation(Up >= 0.f ? Ground(Pos, Up) : Pos, FRotator(0.f, Yaw, 0.f));
	C->SetWorldScale3D(FVector(Scale));
	C->RegisterComponent();
	Placed.Add(C);
	return C;
}

bool AKdkShooterDirector::BeginRound(AKadyktschanPlayerController* InPlayer, int32 Seed)
{
	Player = InPlayer;
	FString Json;
	if (!FFileHelper::LoadFileToString(Json, *(FPaths::ProjectContentDir() / TEXT("Kadykchan/Data/Shooter.json"))) || !Rules.Load(Json))
	{
		UE_LOG(LogKadyktschan, Warning, TEXT("Shooter.json missing or malformed: no shooter mode"));
		return false;
	}
	APawn* Pawn = PlayerPawn();
	if (!Pawn)
	{
		return false;
	}
	Rules.BeginRound(Seed);
	ShotSound = Load<USoundBase>(TEXT("Audio/"), TEXT("A_Shot"));
	ShotFarSound = Load<USoundBase>(TEXT("Audio/"), TEXT("A_ShotFar"));
	ImpactSound = Load<USoundBase>(TEXT("Audio/"), TEXT("A_Impact"));
	GlitchSound = Load<USoundBase>(TEXT("Audio/"), TEXT("A_CamGlitch"));
	ClickSound = Load<USoundBase>(TEXT("Audio/"), TEXT("A_Click"));
	Attenuation = NewObject<USoundAttenuation>(this);
	Attenuation->Attenuation.bAttenuate = true;
	Attenuation->Attenuation.bSpatialize = true;
	Attenuation->Attenuation.AttenuationShapeExtents = FVector(600.f);
	Attenuation->Attenuation.FalloffDistance = 14000.f;  // gunfire carries across the whole centre

	for (const FKdkPlaced& O : Rules.Obstacles)
	{
		if (Place(O.Mesh, O.Pos, O.Yaw, 150.f))
		{
			CoverSpots.Add(O.Pos);
		}
	}
	// flat points hang just under the ceiling lamps: drop onto the table or floor below, never up through the ceiling
	for (const FKdkPickup& P : Rules.Pickups)
	{
		PickupMeshes.Add(Place(ItemMesh(P.Item), P.Pos, FMath::FRandRange(0.f, 360.f), 10.f));
	}
	for (const FKdkTask& T : Rules.Tasks)
	{
		const FString Mesh = T.Kind == TEXT("fetch_flat") ? TEXT("SM_Shooter_Radio") : T.Kind == TEXT("fetch") ? TEXT("SM_Shooter_Documents") : T.Mesh;
		TaskMeshes.Add(Mesh.IsEmpty() ? nullptr : Place(Mesh, T.Pos, FMath::FRandRange(0.f, 360.f), T.Kind == TEXT("destroy") ? 150.f : 10.f));
	}
	SpawnNavigation();

	SavedLocation = Pawn->GetActorLocation();
	SavedRotation = Player->GetControlRotation();
	if (ACharacter* C = Cast<ACharacter>(Pawn))
	{
		// the enemies' rounds trace the visibility channel like the player's own shots
		SavedVisibility = C->GetCapsuleComponent()->GetCollisionResponseToChannel(ECC_Visibility);
		C->GetCapsuleComponent()->SetCollisionResponseToChannel(ECC_Visibility, ECR_Block);
	}
	const FKdkPlaced& S = Rules.Starts[Rules.Start];
	Pawn->SetActorLocation(Ground(S.Pos, 150.f) + FVector(0.f, 0.f, Pawn->GetSimpleCollisionHalfHeight() + 5.f), false, nullptr, ETeleportType::TeleportPhysics);
	Player->SetControlRotation(FRotator(0.f, S.Yaw, 0.f));
	if (AKadyktschanCharacter* C = Cast<AKadyktschanCharacter>(Pawn))
	{
		C->SetShooterMode(true, Rules.Player.Fov);
	}
	bPower = FParse::Param(FCommandLine::Get(), TEXT("KdkPower"));  // dev: the turrets live from the start
	Phase = EPhase::Loading;
	UE_LOG(LogKadyktschan, Display, TEXT("Shooter round %d: %d tasks, %d pickups, %d obstacles, start %d, pick-up %d"), Seed,
		Rules.Tasks.Num(), Rules.Pickups.Num(), CoverSpots.Num(), Rules.Start, Rules.Extract);
	for (int32 I = 0; I < Rules.Tasks.Num(); ++I)  // playtest notes: where this round's tasks and first pickups lie (m)
	{
		UE_LOG(LogKadyktschan, Display, TEXT("Shooter task %d %s at %s"), I, *Rules.Tasks[I].Id, *(Rules.Tasks[I].Pos / 100.0).ToString());
	}
	for (int32 I = 0; I < FMath::Min(3, Rules.Pickups.Num()); ++I)
	{
		UE_LOG(LogKadyktschan, Display, TEXT("Shooter pickup %s in %s at %s"), *Rules.Pickups[I].Item, *Rules.Flats[Rules.Pickups[I].Flat].Where,
			*(Rules.Pickups[I].Pos / 100.0).ToString());
	}
	return true;
}

void AKdkShooterDirector::SpawnNavigation()
{
	UNavigationSystemV1* Nav = FNavigationSystem::GetCurrent<UNavigationSystemV1>(GetWorld());
	if (!Nav)
	{
		UE_LOG(LogKadyktschan, Warning, TEXT("No navigation system: enemies will stand still"));
		return;
	}
	// a bounds volume needs brush geometry, which only the editor builds; a box body gives the same bounds at runtime
	ANavMeshBoundsVolume* Volume = GetWorld()->SpawnActor<ANavMeshBoundsVolume>(Rules.Area.GetCenter(), FRotator::ZeroRotator);
	UBrushComponent* Brush = Volume->GetBrushComponent();
	UBodySetup* Body = NewObject<UBodySetup>(Brush);
	const FVector Size = Rules.Area.GetSize();
	Body->AggGeom.BoxElems.Add(FKBoxElem(Size.X, Size.Y, Size.Z));
	Brush->BrushBodySetup = Body;
	Brush->UpdateBounds();
	Nav->OnNavigationBoundsUpdated(Volume);
	Nav->GetDefaultNavDataInstance(FNavigationSystem::Create);  // runtime generation: Config/DefaultEngine.ini RecastNavMesh
	Spawned.Add(Volume);
}

void AKdkShooterDirector::SpawnEnemies()
{
	if (FParse::Param(FCommandLine::Get(), TEXT("KdkNoEnemies")))  // dev: evidence shots of the camcorder and the props
	{
		return;
	}
	// nothing spawns on top of the player: the first contact comes after a few steps, not at the start
	const FVector From = Rules.Starts[Rules.Start].Pos;
	auto Clear = [&](const FVector& P) { return FVector::Dist2D(P, From) > Rules.SafeStart; };
	for (int32 I = 0; I < Rules.Patrols.Num(); ++I)
	{
		if (!Rules.Patrols[I].IsEmpty() && Clear(Rules.Patrols[I][0]))
		{
			SpawnLooter(Rules.Patrols[I][0], Rules.Patrols[I], false, false);
		}
	}
	// guards wait in three flats: clearing a stairwell is never safe
	for (int32 I = 0; I < 3 && Rules.Flats.Num() > 0; ++I)
	{
		const FKdkFlat& F = Rules.Flats[FMath::RandRange(0, Rules.Flats.Num() - 1)];
		const FVector At = F.Points[FMath::RandRange(0, F.Points.Num() - 1)];
		if (Clear(At)) SpawnLooter(Ground(At, 10.f), {}, true, false);
	}
	for (const FVector& D : Rules.Drones)
	{
		if (Clear(D)) SpawnDrone(D);
	}
	if (const FKdkFighter* T = Rules.Enemies.Find(TEXT("turret")))
	{
		for (const FVector& P : Rules.Turrets)
		{
			if (!Clear(P)) continue;
			const FVector At = Ground(P, 150.f);
			AKdkTurret* Turret = GetWorld()->SpawnActor<AKdkTurret>(At, FRotator(0.f, (Rules.Area.GetCenter() - At).Rotation().Yaw, 0.f));
			if (Turret)
			{
				Turret->Init(this, *T);
				Spawned.Add(Turret);
			}
		}
	}
}

void AKdkShooterDirector::SpawnLooter(const FVector& At, const TArray<FVector>& Patrol, bool bGuard, bool bAlert)
{
	const FKdkFighter* T = Rules.Enemies.Find(TEXT("looter"));
	if (!T)
	{
		return;
	}
	FActorSpawnParameters Params;
	Params.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AdjustIfPossibleButAlwaysSpawn;
	AKdkEnemy* E = GetWorld()->SpawnActor<AKdkEnemy>(Ground(At, bGuard ? 10.f : 150.f) + FVector(0.f, 0.f, 100.f),
		FRotator(0.f, FMath::FRandRange(0.f, 360.f), 0.f), Params);
	if (!E)
	{
		return;
	}
	E->Init(this, TEXT("looter"), *T, Patrol, bGuard);
	Spawned.Add(E);
	if (bAlert && PlayerPawn())
	{
		E->Hear(PlayerPawn()->GetActorLocation());
	}
}

void AKdkShooterDirector::SpawnDrone(const FVector& At)
{
	const FKdkFighter* T = Rules.Enemies.Find(TEXT("drone"));
	if (!T)
	{
		return;
	}
	FActorSpawnParameters Params;
	Params.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AdjustIfPossibleButAlwaysSpawn;
	AKdkEnemy* E = GetWorld()->SpawnActor<AKdkEnemy>(Ground(At, 150.f) + FVector(0.f, 0.f, 50.f), FRotator::ZeroRotator, Params);
	if (!E)
	{
		return;
	}
	// roams one of the looters' routes
	const TArray<FVector> Route = Rules.Patrols.IsEmpty() ? TArray<FVector>() : Rules.Patrols[FMath::RandRange(0, Rules.Patrols.Num() - 1)];
	E->Init(this, TEXT("drone"), *T, Route, false);
	Spawned.Add(E);
}

void AKdkShooterDirector::Reinforce(int32 Looters, int32 Drones)
{
	const APawn* P = PlayerPawn();
	if (!P || Rules.Starts.IsEmpty())
	{
		return;
	}
	// from the road exit farthest from the player: they come down the street, not out of thin air
	int32 Far = 0;
	for (int32 I = 1; I < Rules.Starts.Num(); ++I)
	{
		if (FVector::DistSquared2D(Rules.Starts[I].Pos, P->GetActorLocation()) > FVector::DistSquared2D(Rules.Starts[Far].Pos, P->GetActorLocation()))
		{
			Far = I;
		}
	}
	for (int32 I = 0; I < Looters; ++I)
	{
		SpawnLooter(Rules.Starts[Far].Pos + FVector(I * 150.f, 0.f, 0.f), {}, false, true);
	}
	for (int32 I = 0; I < Drones; ++I)
	{
		SpawnDrone(Rules.Starts[Far].Pos + FVector(0.f, 200.f + I * 150.f, 0.f));
		if (AKdkEnemy* E = Cast<AKdkEnemy>(Spawned.Last()))
		{
			E->Hear(P->GetActorLocation());
		}
	}
}

void AKdkShooterDirector::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	Clock += DeltaSeconds;
	APawn* Pawn = PlayerPawn();
	if (!Pawn || Phase == EPhase::Over)
	{
		return;
	}
	if (Phase == EPhase::Loading)
	{
		// the navigation mesh builds in the background; the enemies come once it is there (or after a minute anyway)
		LoadTime += DeltaSeconds;
		const UNavigationSystemV1* Nav = FNavigationSystem::GetCurrent<UNavigationSystemV1>(GetWorld());
		if ((LoadTime > 2.f && (!Nav || !const_cast<UNavigationSystemV1*>(Nav)->IsNavigationBuildInProgress())) || LoadTime > 60.f)
		{
			UE_LOG(LogKadyktschan, Display, TEXT("Shooter navigation ready after %.1f s"), LoadTime);
			if (FParse::Param(FCommandLine::Get(), TEXT("KdkNavCheck")))  // dev: can the enemies reach every furnished flat?
			{
				int32 Reached = 0;
				UNavigationSystemV1* NavSys = FNavigationSystem::GetCurrent<UNavigationSystemV1>(GetWorld());
				for (const FKdkFlat& F : Rules.Flats)
				{
					// the flat's floor near its first lamp (the lamp itself often hangs over a table)
					FNavLocation Goal;
					const FVector Floor = Ground(F.Points[0], 10.f);
					const bool bOnNav = NavSys && NavSys->ProjectPointToNavigation(Floor, Goal, FVector(150.f, 150.f, 120.f));
					const UNavigationPath* Path = bOnNav ? UNavigationSystemV1::FindPathToLocationSynchronously(GetWorld(),
						Ground(Rules.Starts[Rules.Start].Pos, 150.f), Goal.Location) : nullptr;
					const bool bOk = Path && Path->IsValid() && !Path->IsPartial();
					Reached += bOk;
					UE_LOG(LogKadyktschan, Display, TEXT("Shooter nav check: %s %s (%.0f m, floor %s nav, end %s)"), *F.Where,
						bOk ? TEXT("reachable") : TEXT("NOT reachable"), Path ? Path->GetPathLength() / 100.f : 0.f, bOnNav ? TEXT("on") : TEXT("off"),
						Path && Path->PathPoints.Num() > 0 ? *(Path->PathPoints.Last() / 100.0).ToString() : TEXT("-"));
				}
				UE_LOG(LogKadyktschan, Display, TEXT("Shooter nav check: %d / %d flats reachable from the start"), Reached, Rules.Flats.Num());
				for (const TArray<FVector>& Route : Rules.Patrols)  // outdoor points: in front of each door, then the street
				{
					for (const FVector& P : Route)
					{
						const UNavigationPath* Path = UNavigationSystemV1::FindPathToLocationSynchronously(GetWorld(),
							Ground(Rules.Starts[Rules.Start].Pos, 150.f), Ground(P, 150.f));
						UE_LOG(LogKadyktschan, Display, TEXT("Shooter nav check: patrol point %s %s"), *(P / 100.0).ToString(),
							Path && Path->IsValid() && !Path->IsPartial() ? TEXT("reachable") : TEXT("NOT reachable"));
					}
				}
			}
			SpawnEnemies();
			Phase = EPhase::Running;
		}
		return;
	}
	Rules.Recover(DeltaSeconds);
	Threats.RemoveAll([this](const FThreat& T) { return Clock - T.Time > 1.8f; });
	for (auto It = HitBy.CreateIterator(); It; ++It)
	{
		if (!It.Key().IsValid() || Clock - It.Value() > 2.f) It.RemoveCurrent();
	}
	if (ReloadDone >= 0.f && Clock >= ReloadDone)
	{
		Rules.Reload();
		ReloadDone = -1.f;
		if (AKadyktschanCharacter* C = Cast<AKadyktschanCharacter>(Pawn)) C->SetReloading(false);
	}
	if (bFiring && Clock >= NextShot && ReloadDone < 0.f)
	{
		ShootOnce();
	}

	// what E would use: a pickup, the open task's prop or the power switch, near the view centre and in sight
	FVector Eye;
	FRotator Rot;
	Player->GetPlayerViewPoint(Eye, Rot);
	TArray<FVector> Points;
	TArray<TPair<EFocus, int32>> Ids;
	for (int32 I = 0; I < Rules.Pickups.Num(); ++I)
	{
		if (!Rules.Pickups[I].bTaken && PickupMeshes[I])
		{
			Points.Add(PickupMeshes[I]->GetComponentLocation() + FVector(0.f, 0.f, 10.f));
			Ids.Add({EFocus::Pickup, I});
		}
	}
	if (const FKdkTask* T = Rules.CurrentTask(); T && T->Kind != TEXT("power_on"))
	{
		UStaticMeshComponent* M = TaskMeshes[Rules.Current];
		Points.Add(M ? M->Bounds.Origin : T->Pos);
		Ids.Add({EFocus::Task, Rules.Current});
	}
	Points.Add(Rules.PowerSwitch);
	Ids.Add({EFocus::Switch, 0});
	const int32 Pick = FKdkStory::Pick(Points, Eye, Rot.Vector(), 250.f, 16.f);
	FocusKind = EFocus::None;
	if (Pick != INDEX_NONE)
	{
		FHitResult Hit;
		FCollisionQueryParams Params(SCENE_QUERY_STAT(KdkShooterFocus), true, Pawn);
		Params.AddIgnoredActor(this);  // the props themselves are this actor's components
		if (!GetWorld()->LineTraceSingleByChannel(Hit, Eye, Points[Pick], ECC_Visibility, Params) || Hit.Distance >= FVector::Dist(Eye, Points[Pick]) - 25.f)
		{
			FocusKind = Ids[Pick].Key;
			FocusPickup = Ids[Pick].Value;
			FocusPos = Points[Pick];
		}
	}

	if (Rules.AllTasksDone())
	{
		const FVector Exit = Rules.Starts[Rules.Extract].Pos;
		if (FVector::Dist2D(Pawn->GetActorLocation(), Exit) < 800.f)
		{
			if (!bHoldWave)  // they know where the pick-up is: one last push
			{
				bHoldWave = true;
				Reinforce(Rules.Reinforcements + 1, bWorkshopDown ? 0 : 1);
			}
			HoldLeft -= DeltaSeconds;
			if (HoldLeft <= 0.f)
			{
				Finish(true);
			}
		}
	}
}

bool AKdkShooterDirector::Interact()
{
	if (Phase != EPhase::Running)
	{
		return false;
	}
	switch (FocusKind)
	{
	case EFocus::Pickup:
	{
		const FKdkPickup& P = Rules.Pickups[FocusPickup];
		if (Rules.Take(FocusPickup))
		{
			UE_LOG(LogKadyktschan, Display, TEXT("Shooter: took %s, health %.0f, vest %.0f, reserve %d"), *P.Item, Rules.Health, Rules.Armor, Rules.Reserve);
			PickupMeshes[FocusPickup]->SetVisibility(false);
			Toast(FString::Printf(TEXT("%s genommen."), *ItemName(P.Item)), FString::Printf(TEXT("%s taken."), *ItemName(P.Item)));
		}
		else
		{
			Toast(TEXT("Du bist unverletzt. Es bleibt für später liegen."), TEXT("You are not hurt. It stays here for later."));
		}
		return true;
	}
	case EFocus::Task:
		CompleteTask();
		return true;
	case EFocus::Switch:
	{
		bPower = !bPower;
		Noise(Rules.PowerSwitch, 4000.f);  // the diesel is loud
		const FKdkTask* T = Rules.CurrentTask();
		if (bPower && T && T->Kind == TEXT("power_on"))
		{
			CompleteTask();
		}
		else
		{
			Toast(bPower ? TEXT("Notstrom an: Licht in den Straßen, die Geschütze laufen.") : TEXT("Notstrom aus: dunkel, die Geschütze stehen still."),
				bPower ? TEXT("Backup power on: street lights, the guns are live.") : TEXT("Backup power off: dark, the guns are dead."));
		}
		return true;
	}
	default:
		return false;
	}
}

void AKdkShooterDirector::CompleteTask()
{
	const FKdkTask T = *Rules.CurrentTask();
	UStaticMeshComponent* Prop = TaskMeshes[Rules.Current];
	if (T.Kind == TEXT("fetch_flat") || T.Kind == TEXT("fetch"))
	{
		if (Prop) Prop->SetVisibility(false);
		bIntel |= T.Id == TEXT("intel");
	}
	else if (T.Kind == TEXT("jam"))
	{
		Place(TEXT("SM_Shooter_Jammer"), T.Pos, 0.f, 10.f);
		JamUntil = Clock + Rules.JamTime;
	}
	else if (T.Kind == TEXT("destroy"))
	{
		if (Prop) Prop->SetVisibility(false);
		Place(TEXT("SM_Obs_Scrap"), T.Pos, 0.f, 150.f, 0.5f);
		bWorkshopDown = true;
		Noise(T.Pos, 5000.f);
	}
	const bool bLast = Rules.CompleteTask();
	Toast(T.Done, T.DoneEn);
	Reinforce(Rules.Reinforcements, bWorkshopDown ? 0 : 1);
	if (bLast)
	{
		HoldLeft = Rules.ExtractHold;
	}
}

void AKdkShooterDirector::SetAiming(bool bOn)
{
	bAiming = bOn;
	if (AKadyktschanCharacter* C = Cast<AKadyktschanCharacter>(PlayerPawn()))
	{
		C->SetAiming(bOn, bOn ? Rules.Player.FovAim : Rules.Player.Fov);
	}
}

void AKdkShooterDirector::Reload()
{
	if (Phase != EPhase::Running || ReloadDone >= 0.f || !Rules.CanReload())
	{
		return;
	}
	ReloadDone = Clock + Rules.Player.Reload;
	UGameplayStatics::PlaySound2D(this, ClickSound, 0.7f);
	if (AKadyktschanCharacter* C = Cast<AKadyktschanCharacter>(PlayerPawn())) C->SetReloading(true);
}

void AKdkShooterDirector::ShootOnce()
{
	APawn* Pawn = PlayerPawn();
	if (!Rules.Shoot())
	{
		UGameplayStatics::PlaySound2D(this, ClickSound, 0.8f, 1.3f);
		bFiring = false;
		Toast(TEXT("Magazin leer. R: nachladen."), TEXT("Magazine empty. R: reload."));
		return;
	}
	NextShot = Clock + Rules.Player.Interval;
	FVector Eye;
	FRotator Rot;
	Player->GetPlayerViewPoint(Eye, Rot);
	const FVector Dir = FMath::VRandCone(Rot.Vector(), FMath::DegreesToRadians(PlayerSpread()));
	FHitResult Hit;
	FCollisionQueryParams Params(SCENE_QUERY_STAT(KdkPlayerShot), true, Pawn);
	if (GetWorld()->LineTraceSingleByChannel(Hit, Eye, Eye + Dir * Rules.Player.Range, ECC_Visibility, Params))
	{
		AActor* A = Hit.GetActor();
		if (A && (A->IsA<AKdkEnemy>() || A->IsA<AKdkTurret>()))
		{
			float Damage = Rules.Player.Damage;
			if (const ACharacter* C = Cast<ACharacter>(A); C && Hit.ImpactPoint.Z > C->GetActorLocation().Z + C->GetSimpleCollisionHalfHeight() - 30.f)
			{
				Damage *= 2.5f;  // head
			}
			A->TakeDamage(Damage, FPointDamageEvent(Damage, Hit, Dir, nullptr), Player.Get(), Pawn);
			// hit marker and tick: a short cross around the crosshair; red and a duller thud for a takedown
			const AKdkEnemy* E = Cast<AKdkEnemy>(A);
			const AKdkTurret* T = Cast<AKdkTurret>(A);
			bKillMark = (E && E->IsDead()) || (T && T->IsDead());
			HitMarkUntil = Clock + (bKillMark ? 0.4f : 0.2f);
			UGameplayStatics::PlaySound2D(this, ImpactSound, bKillMark ? 1.f : 0.7f, bKillMark ? 0.8f : 1.7f);
		}
		PlayAt(ImpactSound, Hit.ImpactPoint, 0.6f);
	}
	UGameplayStatics::PlaySound2D(this, ShotSound, 1.8f, FMath::FRandRange(0.96f, 1.04f));
	Noise(Pawn->GetActorLocation(), Rules.Player.Noise);
	FRotator Kick = Player->GetControlRotation();  // recoil walks the muzzle up
	Kick.Pitch += FMath::FRandRange(0.35f, 0.7f) * (bAiming ? 0.6f : 1.f);
	Kick.Yaw += FMath::FRandRange(-0.3f, 0.3f);
	Player->SetControlRotation(Kick);
	if (AKadyktschanCharacter* C = Cast<AKadyktschanCharacter>(Pawn)) C->ShotFx();
}

float AKdkShooterDirector::PlayerSpread() const
{
	const APawn* Pawn = PlayerPawn();
	const float Speed = Pawn ? Pawn->GetVelocity().Size2D() : 0.f;
	return (bAiming ? Rules.Player.Spread : Rules.Player.SpreadHip) * (1.f + Speed / 450.f);
}

bool AKdkShooterDirector::PlayerVisibleFrom(const FVector& Eye, const AActor* Ignore, FVector& OutTarget) const
{
	const APawn* P = PlayerPawn();
	if (!P || !Player.IsValid() || !Player->PlayerCameraManager)
	{
		return false;
	}
	FCollisionQueryParams Params(SCENE_QUERY_STAT(KdkPlayerVisible), true, Ignore);
	const FVector Head = Player->PlayerCameraManager->GetCameraLocation() - FVector(0.f, 0.f, 8.f);
	const FVector Chest = P->GetActorLocation() + FVector(0.f, 0.f, 20.f);
	bool bSeen = false;
	for (const FVector& Point : FMath::RandBool() ? TArray<FVector>{Head, Chest} : TArray<FVector>{Chest, Head})
	{
		FHitResult Hit;
		if (!GetWorld()->LineTraceSingleByChannel(Hit, Eye, Point, ECC_Visibility, Params) || Hit.GetActor() == P
			|| Hit.Distance >= FVector::Dist(Eye, Point) - 20.f)
		{
			OutTarget = Point;
			bSeen = true;
			break;
		}
	}
	return bSeen;
}

bool AKdkShooterDirector::RequestFireToken(const AActor* Shooter)
{
	FireTokens.RemoveAll([this](const TPair<TWeakObjectPtr<const AActor>, float>& T) { return !T.Key.IsValid() || T.Value < Clock; });
	for (TPair<TWeakObjectPtr<const AActor>, float>& T : FireTokens)
	{
		if (T.Key.Get() == Shooter)
		{
			T.Value = Clock + 2.5f;
			return true;
		}
	}
	if (FireTokens.Num() >= Rules.MaxShooters)
	{
		return false;
	}
	FireTokens.Add({Shooter, Clock + 2.5f});
	return true;
}

bool AKdkShooterDirector::FindFightSpot(const AActor* Enemy, const FKdkFighter& Tuning, bool bFlank, FVector& OutSpot, FVector& OutPeek, bool& bOutCover)
{
	const APawn* P = PlayerPawn();
	UNavigationSystemV1* Nav = FNavigationSystem::GetCurrent<UNavigationSystemV1>(GetWorld());
	if (!P || !Nav)
	{
		return false;
	}
	const FVector Target = P->GetActorLocation();  // the player
	const FVector Head = Target + FVector(0.f, 0.f, 60.f);
	const FVector From = Enemy->GetActorLocation();
	const FVector Line = (From - Target).GetSafeNormal2D();  // player -> enemy: flanking leaves this line
	const float Ideal = (Tuning.EngageMin + Tuning.EngageMax) * 0.5f;
	FCollisionQueryParams Params(SCENE_QUERY_STAT(KdkFightSpot), true, P);  // obstacles (this actor's components) do block
	Params.AddIgnoredActor(Enemy);
	auto Clear = [&](const FVector& A, const FVector& B)
	{
		FHitResult Hit;
		return !GetWorld()->LineTraceSingleByChannel(Hit, A, B, ECC_Visibility, Params);
	};
	float Best = TNumericLimits<float>::Max();
	auto Consider = [&](const FVector& Spot, const FVector& Peek, bool bCover)
	{
		const float D = FVector::Dist2D(Spot, Target);
		FNavLocation OnNav;
		if (D < Tuning.EngageMin || D > Tuning.EngageMax || !Nav->ProjectPointToNavigation(Spot, OnNav, FVector(80.f, 80.f, 200.f)))
		{
			return;
		}
		// short way there, near the ideal distance, cover first, off the line when flanking, away from the others
		float Score = FVector::Dist2D(From, Spot) / 100.f + FMath::Abs(D - Ideal) / 200.f + (bCover ? -12.f : 0.f) + FMath::FRand() * 3.f;
		if (bFlank)
		{
			Score += FVector::DotProduct((Spot - Target).GetSafeNormal2D(), Line) * 15.f;
		}
		for (const TPair<TWeakObjectPtr<const AActor>, FVector>& C : Claims)
		{
			if (C.Key.IsValid() && C.Key.Get() != Enemy && FVector::Dist2D(C.Value, Spot) < 500.f)
			{
				Score += 20.f;
			}
		}
		if (Score < Best)
		{
			Best = Score;
			OutSpot = OnNav.Location;
			OutPeek = Peek;
			bOutCover = bCover;
		}
	};
	// behind an obstacle as seen from the player, hidden; a step to one side clears the view for the shots
	for (const FVector& Spot : CoverSpots)
	{
		if (FVector::Dist2D(Spot, From) > 4500.f)
		{
			continue;
		}
		const FVector Away = (Spot - Target).GetSafeNormal2D();
		const FVector Hide = Ground(Spot + Away * 190.f, 150.f) + FVector(0.f, 0.f, 90.f);
		if (Clear(Hide + FVector(0.f, 0.f, 30.f), Head))
		{
			continue;  // the player would see it there
		}
		const FVector Side(-Away.Y, Away.X, 0.f);
		for (const float Sign : {1.f, -1.f})
		{
			const FVector Peek = Ground(Spot + Away * 190.f + Side * Sign * 170.f, 150.f) + FVector(0.f, 0.f, 90.f);
			if (Clear(Peek + FVector(0.f, 0.f, 40.f), Head))
			{
				Consider(Hide, Peek, true);
				break;
			}
		}
	}
	// open ground on a ring around the player, with a clear view
	for (int32 K = 0; K < 12; ++K)
	{
		const float A = 2.f * PI * (K + FMath::FRand()) / 12.f;
		const FVector Spot = Ground(Target + FVector(FMath::Cos(A), FMath::Sin(A), 0.f) * Ideal * FMath::FRandRange(0.8f, 1.2f), 300.f) + FVector(0.f, 0.f, 90.f);
		if (Clear(Spot + FVector(0.f, 0.f, 40.f), Head))
		{
			Consider(Spot, Spot, false);
		}
	}
	if (Best == TNumericLimits<float>::Max())
	{
		return false;
	}
	Claims.Add(Enemy, OutSpot);
	return true;
}

void AKdkShooterDirector::FireAt(AActor* Shooter, const FVector& Muzzle, const FKdkFighter& Tuning, float SpreadScale)
{
	APawn* P = PlayerPawn();
	if (!P || Phase != EPhase::Running)
	{
		return;
	}
	FVector Target;
	if (!PlayerVisibleFrom(Muzzle, Shooter, Target))
	{
		Target = P->GetActorLocation() + FVector(0.f, 0.f, 20.f);  // lost sight a moment ago: into the cover
	}
	const float Dist = FVector::Dist(Target, Muzzle);
	const ACharacter* C = Cast<ACharacter>(P);
	// farther, faster or crouched is harder to hit
	const float Spread = Tuning.Spread * (0.6f + Dist / FMath::Max(Tuning.Range, 1.f)) * (1.f + P->GetVelocity().Size2D() / 500.f)
		* (C && C->bIsCrouched ? 0.75f : 1.f) * SpreadScale;
	const FVector Dir = FMath::VRandCone((Target - Muzzle).GetSafeNormal(), FMath::DegreesToRadians(Spread));
	FHitResult Hit;
	FCollisionQueryParams Params(SCENE_QUERY_STAT(KdkEnemyShot), true, Shooter);
	const bool bHit = GetWorld()->LineTraceSingleByChannel(Hit, Muzzle, Muzzle + Dir * (Dist + 2000.f), ECC_Visibility, Params);
	PlayAt(Dist > 2500.f ? ShotFarSound : ShotSound, Muzzle, 1.6f);
	if (bHit && Hit.GetActor() == P)
	{
		Threats.Add({Muzzle, Clock, 1.f});
		HitBy.Add(Shooter, Clock);  // marked above its head for 2 s (user 2026-11-11)
		DamagePlayer(Tuning.Damage);
	}
	else if (bHit && FVector::Dist(Hit.ImpactPoint, P->GetActorLocation()) < 800.f)
	{
		Threats.Add({Muzzle, Clock, 0.45f});  // near miss: you hear it and see where from
		PlayAt(ImpactSound, Hit.ImpactPoint, 1.2f);
	}
}

void AKdkShooterDirector::DamagePlayer(float Damage)
{
	if (Phase != EPhase::Running)
	{
		return;
	}
	Rules.Hit(Damage);
	++HitsTaken;
	UGameplayStatics::PlaySound2D(this, GlitchSound, 0.8f);
	if (Player.IsValid())
	{
		Player->OnShooterHurt();
	}
	if (Rules.IsDown())
	{
		Finish(false);
	}
}

void AKdkShooterDirector::Noise(const FVector& At, float Radius)
{
	for (AActor* A : Spawned)
	{
		AKdkEnemy* E = Cast<AKdkEnemy>(A);
		if (E && !E->IsDead() && FVector::Dist(E->GetActorLocation(), At) < Radius)
		{
			E->Hear(At);
		}
	}
}

void AKdkShooterDirector::OnEnemyDown()
{
	++Kills;
}

bool AKdkShooterDirector::FindCover(const FVector& From, float MaxDist, FVector& Out) const
{
	const APawn* P = PlayerPawn();
	if (!P)
	{
		return false;
	}
	const FVector Eye = P->GetActorLocation() + FVector(0.f, 0.f, 60.f);
	float Best = MaxDist;
	bool bFound = false;
	FCollisionQueryParams Params(SCENE_QUERY_STAT(KdkCover), true, P);
	for (const FVector& Spot : CoverSpots)
	{
		const float D = FVector::Dist2D(Spot, From);
		if (D >= Best)
		{
			continue;
		}
		// the far side of the obstacle, seen from the player, and the obstacle really between the two
		const FVector Behind = Ground(Spot + (Spot - P->GetActorLocation()).GetSafeNormal2D() * 220.f, 150.f) + FVector(0.f, 0.f, 80.f);
		FHitResult Hit;
		if (GetWorld()->LineTraceSingleByChannel(Hit, Eye, Behind, ECC_Visibility, Params))
		{
			Best = D;
			Out = Behind;
			bFound = true;
		}
	}
	return bFound;
}

void AKdkShooterDirector::Finish(bool bWon)
{
	Phase = EPhase::Over;
	bFiring = false;
	const FString Stats = FString::Printf(TEXT("%s %s   ·   %s %d   ·   %s %d"), *KdkLoc::S(TEXT("Zeit"), TEXT("Time")), *FormatTime(Clock - LoadTime),
		*KdkLoc::S(TEXT("Gegner ausgeschaltet"), TEXT("Enemies down")), Kills, *KdkLoc::S(TEXT("Treffer abbekommen"), TEXT("Hits taken")), HitsTaken);
	const FString Title = bWon ? KdkLoc::S(TEXT("EINSATZ ERFÜLLT"), TEXT("MISSION COMPLETE")) : KdkLoc::S(TEXT("SIGNAL VERLOREN"), TEXT("SIGNAL LOST"));
	const FString Text = (bWon ? KdkLoc::S(TEXT("Abgeholt. Die Aufnahme endet hier."), TEXT("Picked up. The recording ends here."))
		: KdkLoc::S(TEXT("Die Kamera zeigt nur noch Rauschen."), TEXT("The camera shows nothing but noise."))) + TEXT("\n\n") + Stats
		+ KdkLoc::S(TEXT("\n\n[E]  Zurück zum Hauptmenü"), TEXT("\n\n[E]  Back to the main menu"));
	if (Player.IsValid())
	{
		Player->ShowShooterResult(Title, Text);
	}
	UE_LOG(LogKadyktschan, Display, TEXT("Shooter round over: %s, %s"), bWon ? TEXT("won") : TEXT("lost"), *Stats);
}

void AKdkShooterDirector::Toast(const FString& De, const FString& En)
{
	ToastText = KdkLoc::S(De, En);
	ToastUntil = Clock + 4.f;
}

void AKdkShooterDirector::PlayAt(USoundBase* Sound, const FVector& At, float Volume) const
{
	if (Sound)
	{
		UGameplayStatics::PlaySoundAtLocation(this, Sound, At, Volume, FMath::FRandRange(0.94f, 1.06f), 0.f, Attenuation);
	}
}

void AKdkShooterDirector::FillHud(FKdkShooterHud& Out) const
{
	Out = FKdkShooterHud();
	if (Phase == EPhase::Loading)
	{
		Out.Header = KdkLoc::S(TEXT("EINSATZ   ·   VERBINDUNG WIRD AUFGEBAUT …"), TEXT("MISSION   ·   ESTABLISHING LINK …"));
		Out.Goal = KdkLoc::S(TEXT("Die Plünderer bemerken dich gleich. Sieh dich um."), TEXT("The looters will notice you shortly. Look around."));
		return;
	}
	if (Phase == EPhase::Over)
	{
		Out.Header = KdkLoc::S(TEXT("EINSATZ BEENDET"), TEXT("MISSION OVER"));
		return;
	}
	const FString Ammo = FString::Printf(TEXT("%d / %d"), Rules.Mag, Rules.Reserve);
	FString Jam = IsJammed() ? FString::Printf(TEXT("   ·   %s %d s"), *KdkLoc::S(TEXT("STÖRSENDER"), TEXT("JAMMER")), FMath::CeilToInt(JamUntil - Clock)) : FString();
	if (const AKadyktschanCharacter* C = Cast<AKadyktschanCharacter>(PlayerPawn()); C && C->IsInCover())
	{
		Jam += KdkLoc::S(TEXT("   ·   IN DECKUNG (Q)"), TEXT("   ·   IN COVER (Q)"));
	}
	Out.Spread = PlayerSpread();
	Out.Health = Rules.Health / FMath::Max(1.f, Rules.Player.Health);
	for (const TPair<TWeakObjectPtr<AActor>, float>& H : HitBy)
	{
		const AActor* A = H.Key.Get();
		const float Age = Clock - H.Value;
		const AKdkEnemy* E = Cast<AKdkEnemy>(A);
		const AKdkTurret* T = Cast<AKdkTurret>(A);
		if (A && Age < 2.f && !(E && E->IsDead()) && !(T && T->IsDead()))
		{
			const FVector Above = A->GetActorLocation() + FVector(0.f, 0.f, E ? A->GetSimpleCollisionHalfHeight() + 35.f : 190.f);
			Out.Marks.Add(FVector4f(FVector3f(Above), 1.f - FMath::Max(0.f, Age - 1.5f) / 0.5f));  // full for 1.5 s, then fading
		}
	}
	for (const FThreat& T : Threats)
	{
		const float Age = Clock - T.Time;
		if (Age < 1.8f)
		{
			Out.Threats.Add(FVector4f(FVector3f(T.From), T.Strength * (1.f - Age / 1.8f)));
		}
	}
	Out.HitMarker = HitMarkUntil > Clock ? FMath::Clamp((HitMarkUntil - Clock) / (bKillMark ? 0.4f : 0.2f), 0.f, 1.f) : 0.f;
	Out.bKill = bKillMark;
	if (const FKdkTask* T = Rules.CurrentTask())
	{
		Out.Header = FString::Printf(TEXT("%s %d / %d   ·   %s %s%s"), *KdkLoc::S(TEXT("AUFTRAG"), TEXT("TASK")), Rules.Current + 1, Rules.Tasks.Num(),
			*KdkLoc::S(TEXT("MAGAZIN"), TEXT("MAGAZINE")), *Ammo, *Jam);
		Out.Goal = KdkLoc::S(T->Goal, T->GoalEn);
		Out.bMarker = true;
		Out.Target = T->Kind == TEXT("power_on") ? Rules.PowerSwitch : T->Pos;
	}
	else
	{
		Out.Header = FString::Printf(TEXT("%s   ·   %s %s%s"), *KdkLoc::S(TEXT("ABHOLUNG"), TEXT("PICK-UP")), *KdkLoc::S(TEXT("MAGAZIN"), TEXT("MAGAZINE")), *Ammo, *Jam);
		Out.Goal = FString::Printf(TEXT("%s %d s."), *KdkLoc::S(TEXT("Zum Abholpunkt am Stadtrand. Halte dort durch:"),
			TEXT("Get to the pick-up point at the edge of town. Hold out there:")), FMath::CeilToInt(FMath::Max(0.f, HoldLeft)));
		Out.bMarker = true;
		Out.Target = Rules.Starts[Rules.Extract].Pos;
	}
	switch (FocusKind)
	{
	case EFocus::Pickup:
		Out.Prompt = FString::Printf(TEXT("[E]  %s"), *ItemName(Rules.Pickups[FocusPickup].Item));
		break;
	case EFocus::Task:
		Out.Prompt = FString::Printf(TEXT("[E]  %s"), *KdkLoc::S(Rules.Tasks[FocusPickup].Kind == TEXT("jam") ? TEXT("Störsender anbringen")
			: Rules.Tasks[FocusPickup].Kind == TEXT("destroy") ? TEXT("Werkstatt zerstören") : TEXT("Mitnehmen"),
			Rules.Tasks[FocusPickup].Kind == TEXT("jam") ? TEXT("Fit the jammer") : Rules.Tasks[FocusPickup].Kind == TEXT("destroy") ? TEXT("Wreck the workshop") : TEXT("Take")));
		break;
	case EFocus::Switch:
		Out.Prompt = FString::Printf(TEXT("[E]  %s"), *KdkLoc::S(bPower ? TEXT("Notstrom abschalten") : TEXT("Notstrom starten"), bPower ? TEXT("Shut down backup power") : TEXT("Start backup power")));
		break;
	default:
		break;
	}
	Out.bFocus = FocusKind != EFocus::None;
	Out.Focus = FocusPos;
	if (!Out.bFocus)
	{
		if (ReloadDone >= 0.f) Out.Prompt = KdkLoc::S(TEXT("Nachladen …"), TEXT("Reloading …"));
		else if (Clock < ToastUntil) Out.Prompt = ToastText;
	}
	if (bIntel)  // the situation map: looters close by are marked
	{
		const APawn* P = PlayerPawn();
		for (AActor* A : Spawned)
		{
			const AKdkEnemy* E = Cast<AKdkEnemy>(A);
			if (E && !E->IsDead() && P && FVector::Dist(E->GetActorLocation(), P->GetActorLocation()) < 8000.f)
			{
				Out.Rings.Add(E->GetActorLocation() + FVector(0.f, 0.f, 60.f));
			}
		}
	}
}

void AKdkShooterDirector::EndRound()
{
	if (bEnded)
	{
		return;
	}
	bEnded = true;
	for (AActor* A : Spawned)
	{
		if (!IsValid(A)) continue;
		if (const APawn* Pawn = Cast<APawn>(A); Pawn && Pawn->GetController())
		{
			Pawn->GetController()->Destroy();
		}
		A->Destroy();
	}
	Spawned.Reset();
	for (UStaticMeshComponent* C : Placed)
	{
		if (IsValid(C)) C->DestroyComponent();
	}
	Placed.Reset();
	if (APawn* Pawn = PlayerPawn())
	{
		if (ACharacter* C = Cast<ACharacter>(Pawn))
		{
			C->GetCapsuleComponent()->SetCollisionResponseToChannel(ECC_Visibility, SavedVisibility);
			C->UnCrouch();
		}
		if (AKadyktschanCharacter* C = Cast<AKadyktschanCharacter>(Pawn))
		{
			C->SetShooterMode(false, 0.f);
		}
		Pawn->SetActorLocation(SavedLocation, false, nullptr, ETeleportType::TeleportPhysics);
		Player->SetControlRotation(SavedRotation);
	}
}

void AKdkShooterDirector::Destroyed()
{
	EndRound();
	Super::Destroyed();
}
