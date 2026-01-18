import typing as t
from datetime import datetime, timedelta

from coordimeet.events.models import Event, EventCalendarTypeChoices


class EventServices:
    @staticmethod
    def get_best_date_range(event: Event) -> t.List[t.Dict[str, t.Union[datetime, int]]]:
        """Return the best date range for an event. The same function as in Event.vue"""
        date_count_map = {}
        calendar_type = event.event_calendar_type

        for range in event.event_availability_options.all():
            current_date = range.start_date
            end_date = range.end_date

            while current_date <= end_date:
                date_string = current_date.isoformat()
                date_count_map[date_string] = date_count_map.get(date_string, 0) + 1
                current_date += timedelta(days=1) if calendar_type == EventCalendarTypeChoices.DATE else timedelta(hours=1)

        result = []
        date_count_keys = sorted(date_count_map.keys())

        for start_date in date_count_keys:
            end_date = datetime.fromisoformat(start_date) + (
                timedelta(days=event.event_length) if calendar_type == EventCalendarTypeChoices.DATE else timedelta(hours=event.event_length)
            )
            if end_date.isoformat() not in date_count_keys:
                continue

            hits = 0
            current_date = datetime.fromisoformat(start_date)
            while current_date < end_date:
                hits += date_count_map.get(current_date.isoformat(), 0)
                current_date += timedelta(days=1) if calendar_type == EventCalendarTypeChoices.DATE else timedelta(hours=1)

            result.append({
                "range": {
                    "start_date": datetime.fromisoformat(start_date),
                    "end_date": end_date,
                },
                "hits": hits,
            })

        # if there are no results, return the first available date
        if not result:
            first_range = event.event_availability_options.order_by("start_date").first()
            end_date = first_range.start_date + timedelta(days=event.event_length) if calendar_type == EventCalendarTypeChoices.DATE else timedelta(hours=event.event_length)
            return [{
                "range": {
                    "start_date": first_range.start_date,
                    "end_date": end_date,
                },
                "hits": 0,
            }]

        return sorted(result, key=lambda x: x["hits"], reverse=True)
