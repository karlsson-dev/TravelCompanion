from domain.repositories import UserHistoryRepository
from domain.services.visit_service import VisitService
from api.schemas import VisitCreate
from infrastructure.external.foursquare_client import search_places, parse_place_item, foursquare_category_id


class RecommendationEngine:
    def __init__(self, session):
        self.session = session

    async def recommend(self, user_id: int, latitude: float, longitude: float, radius: int = 2000):
        repo = UserHistoryRepository(self.session)
        history = await repo.get_user_history(user_id)

        visited_place_ids = {h.place_id for h in history}
        liked_categories = [h.category for h in history if h.rating and h.rating >= 7]
        min_rating = min((h.rating for h in history if h.rating), default=0)

        categories = liked_categories or ["Arts & Entertainment", "Restaurants"]

        recommendations = []
        new_visits = []

        for category in categories:
            category_id = foursquare_category_id(category)
            if not category_id:
                continue

            params = {
                "ll": f"{latitude},{longitude}",
                "radius": radius,
                "categories": category_id,
                "sort": "RELEVANCE",
                "limit": 20
            }

            response = await search_places(params)
            results = response.get("results", [])

            for item in results:
                parsed = parse_place_item(item, min_rating)
                if parsed and parsed["external_id"] not in visited_place_ids:
                    parsed["category"] = category
                    parsed["rating"] = item.get("rating", 0)
                    recommendations.append(parsed)

                    # Подготовим к сохранению в Visit
                    visit = VisitCreate(
                        user_id=user_id,
                        external_id=parsed["external_id"],
                        name=parsed["name"],
                        latitude=parsed["latitude"],
                        longitude=parsed["longitude"],
                        address=parsed["address"],
                        category=parsed.get("category")
                    )
                    new_visits.append(visit)

        # Сохраняем новые визиты в visit_service
        visit_service = VisitService(self.session)
        for visit in new_visits:
            await visit_service.create_visit(visit)

        recommendations.sort(key=lambda x: x["rating"], reverse=True)
        return recommendations[:10]

    async def mark_as_visited(self, user_id: int, recommendation: dict):
        """
        Метод для сохранения информации о посещенном месте в историю пользователя.
        """
        try:
            visit = VisitCreate(
                user_id=user_id,
                external_id=recommendation["external_id"],
                name=recommendation["name"],
                latitude=recommendation["latitude"],
                longitude=recommendation["longitude"],
                address=recommendation["address"],
                category=recommendation.get("category")
            )

            # Создание визита через VisitService
            visit_service = VisitService(self.session)
            return await visit_service.create_visit(visit)
        except Exception as e:
            raise ValueError(f"Ошибка при сохранении места: {str(e)}")
