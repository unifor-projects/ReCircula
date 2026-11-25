import { PackageCheck } from 'lucide-react';

export default function DoadoLockerBadge() {
  return (
    <span className="inline-flex items-center gap-1 rounded-full bg-emerald-600 px-2.5 py-0.5 text-xs font-semibold text-white shadow-sm ring-2 ring-emerald-200">
      <PackageCheck size={13} aria-hidden="true" />
      Doado no locker
    </span>
  );
}
