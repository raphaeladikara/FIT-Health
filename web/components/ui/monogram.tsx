import { caseToken, triageTone } from "@/lib/triage";

/**
 * Anonymised case chip. Shows a non-identifying token derived from the
 * generated case id only — never a name, initials of a person, or a photo.
 */
export function Monogram({
  caseId,
  category,
  size = "md",
}: {
  caseId: string;
  category: string;
  size?: "sm" | "md";
}) {
  return (
    <span
      className="monogram"
      data-size={size}
      data-tone={triageTone(category)}
      aria-hidden="true"
    >
      {caseToken(caseId)}
    </span>
  );
}
