"""Workforce allocation by class within a district.

Jobs are filled in priority order. A job first takes workers of its own class,
then progressively higher classes at reduced efficiency. Lower classes never
fill higher-class jobs.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Job:
    key: str               # e.g. "kiln_1" or "nursery_1#research"
    holder_id: str
    job_class: str
    required: float
    priority: int
    order: int


@dataclass
class Allocation:
    staffing: dict[str, float] = field(default_factory=dict)      # job key -> 0..1
    employed: dict[str, float] = field(default_factory=dict)      # class -> WP used
    demand: dict[str, float] = field(default_factory=dict)        # class -> WP required by jobs of that class
    vacancies: dict[str, float] = field(default_factory=dict)     # class -> effective WP still unfilled
    remaining: dict[str, float] = field(default_factory=dict)     # class -> WP unassigned
    below_class: dict[str, float] = field(default_factory=dict)   # class -> WP filling lower-class jobs


def allocate(supply: dict[str, float], jobs: list[Job], classes: list[str], efficiency: list[float]) -> Allocation:
    remaining = {job_class: float(supply.get(job_class, 0.0)) for job_class in classes}
    result = Allocation(
        employed={c: 0.0 for c in classes},
        demand={c: 0.0 for c in classes},
        vacancies={c: 0.0 for c in classes},
        below_class={c: 0.0 for c in classes},
    )
    for job in sorted(jobs, key=lambda j: (j.priority, j.order, j.key)):
        job_index = classes.index(job.job_class)
        need = float(job.required)
        result.demand[job.job_class] += need
        for worker_index in range(job_index, len(classes)):
            if need <= 1e-9:
                break
            worker_class = classes[worker_index]
            eff = efficiency[worker_index - job_index]
            used = min(remaining[worker_class], need / eff)
            remaining[worker_class] -= used
            result.employed[worker_class] += used
            if worker_index > job_index:
                result.below_class[worker_class] += used
            need -= used * eff
        need = max(0.0, need)
        result.vacancies[job.job_class] += need
        result.staffing[job.key] = (job.required - need) / job.required if job.required else 1.0
    result.remaining = remaining
    return result
