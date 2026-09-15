import type { Activity } from "@/types/api";

const KIND_LABELS: Record<Activity["kind"], string> = {
  trail: "Trail",
  tour: "Tour",
};

export default function ActivityList({ activities }: { activities: Activity[] }) {
  if (activities.length === 0) {
    return <p className="text-asphalt">No trails or tours on file for this spot yet.</p>;
  }

  return (
    <ul className="flex flex-col divide-y divide-asphalt/20 border-t border-asphalt/20">
      {activities.map((activity) => (
        <li key={activity.name} className="flex items-baseline justify-between gap-4 py-3">
          <span className="text-ink">
            {activity.name}
            {activity.permit_required && (
              <span className="ml-2 text-sm text-signal">Permit required</span>
            )}
          </span>
          <span className="figure shrink-0 text-sm text-asphalt">
            {KIND_LABELS[activity.kind]}
            {activity.distance_mi ? `, ${activity.distance_mi} mi` : ""}
            {activity.elevation_gain_ft ? `, ${activity.elevation_gain_ft} ft gain` : ""}
          </span>
        </li>
      ))}
    </ul>
  );
}
