import { VerificationStatus } from '../types';

export function getVerificationBadge(status: VerificationStatus): {
  label: string;
  badgeClass: string;
  iconName: string;
  description: string;
} {
  switch (status) {
    case 'SUPPORTED':
      return {
        label: 'SUPPORTED',
        badgeClass: 'bg-emerald-950/80 border-emerald-500/50 text-emerald-300',
        iconName: 'CheckCircle2',
        description: 'Directly corroborated by authoritative primary source empirical data.',
      };
    case 'CONTRADICTED':
      return {
        label: 'CONTRADICTED',
        badgeClass: 'bg-rose-950/80 border-rose-500/50 text-rose-300',
        iconName: 'XCircle',
        description: 'Directly refuted by opposing factual statistics or institutional records.',
      };
    case 'PARTIALLY_SUPPORTED':
      return {
        label: 'PARTIALLY SUPPORTED',
        badgeClass: 'bg-amber-950/80 border-amber-500/50 text-amber-300',
        iconName: 'AlertCircle',
        description: 'Aspects of the claim are confirmed, but scope or magnitude lacks full backing.',
      };
    case 'CONFLICTING_EVIDENCE':
      return {
        label: 'CONFLICTING EVIDENCE',
        badgeClass: 'bg-purple-950/80 border-purple-500/50 text-purple-300',
        iconName: 'Scale',
        description: 'Credible sources present divergent statistics due to date, scope, or sample differences.',
      };
    case 'INSUFFICIENT_EVIDENCE':
    default:
      return {
        label: 'INSUFFICIENT EVIDENCE',
        badgeClass: 'bg-slate-900 border-slate-700 text-slate-400',
        iconName: 'HelpCircle',
        description: 'Available source snippets do not contain sufficient empirical data to verify.',
      };
  }
}

export function formatDate(dateString: string): string {
  try {
    const d = new Date(dateString);
    return d.toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return dateString;
  }
}
