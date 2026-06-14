import { ShieldOff } from "lucide-react";

export function ClaimBoundary({ text }: { text: string }) {
  return (
    <div className="claim-boundary">
      <p className="claim-boundary-head">
        <ShieldOff aria-hidden="true" size={15} />
        What we cannot claim
      </p>
      <p className="claim-boundary-text">{text}</p>
    </div>
  );
}
