import { useState } from "react";
import type { Claim } from "./api";
import { api, errorMessage } from "./api";
import { money } from "./format";
import { useData } from "./hooks";

interface Props {
  claim: Claim;
  onChange: () => void;
}

/** Sign off a payout over the limit, which releases the payment. */
export function SignOff({ claim, onChange }: Readonly<Props>) {
  const { data: handlers } = useData(api.handlers, 0);
  const [handlerId, setHandlerId] = useState("");
  const [error, setError] = useState<string>();
  const payout = money(claim.decision?.payout ?? 0);
  const signOff = () => {
    api.signOff(claim.claim_id, handlerId).then(onChange, (reason: unknown) => {
      setError(errorMessage(reason));
    });
  };
  return (
    <div className="sign-off">
      <h3>Waiting for sign-off</h3>
      <p>
        The payout of <span className="mono">{payout}</span> is over $1,000, so
        it is held until a handler signs off.
      </p>
      <label htmlFor="handler">Handler</label>
      <select
        id="handler"
        value={handlerId}
        onChange={(event) => {
          setHandlerId(event.target.value);
        }}
      >
        <option value="">Choose a handler</option>
        {handlers
          ?.filter((h) => h.can_approve_over_limit)
          .map((h) => (
            <option key={h.handler_id} value={h.handler_id}>
              {h.name}
            </option>
          ))}
      </select>
      <button
        type="button"
        className="primary"
        disabled={!handlerId}
        onClick={signOff}
      >
        Sign off and pay {payout}
      </button>
      {error && <p className="error">{error}</p>}
    </div>
  );
}
