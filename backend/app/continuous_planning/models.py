from enum import Enum
class PlanningCycleStatus(str,Enum): scheduled='scheduled'; running='running'; completed='completed'; blocked='blocked'; failed='failed'; canceled='canceled'
class RecommendationStatus(str,Enum): proposed='proposed'; under_review='under_review'; approved='approved'; rejected='rejected'; archived='archived'
class DecisionLineageEventType(str,Enum): decision_created='decision_created'; assumption_added='assumption_added'; evidence_added='evidence_added'; recommendation_created='recommendation_created'; recommendation_approved='recommendation_approved'; recommendation_rejected='recommendation_rejected'; strategy_changed='strategy_changed'; roadmap_changed='roadmap_changed'; outcome_recorded='outcome_recorded'
