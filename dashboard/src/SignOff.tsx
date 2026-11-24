import { useEffect, useState, type SubmitEvent } from "react";
import { api, type Handler } from "./api";
import { message, money } from "./format";

interface Props {
  claimId: string;
  payout: number;
  signedOff: boolean;
  onChange: () => void;
}

export function SignOff({
  claimId,
  payout,
  signedOff,
  onChange,
}: Readonly<Props>) {
  const [handlers, setHandlers] = useState<Handler[]>([]);
  const [handlerId, setHandlerId] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .handlers()
      .then((all) => {
        const allowed = all.filter((handler) => handler.can_sign_off);
        setHandlers(allowed);
        setHandlerId(allowed[0]?.handler_id ?? "");
      })
      .catch((reason: unknown) => {
        setError(message(reason));
      });
  }, []);

  async function signOffAndPay() {
    if (!signedOff) await api.signOff(claimId, handlerId);
    await api.pay(claimId, payout);
  }

  function submit(event: SubmitEvent) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    signOffAndPay()
      .catch((reason: unknown) => {
        setError(message(reason));
      })
      .finally(() => {
        setBusy(false);
        onChange();
      });
  }

  return (
    <form className="signoff" onSubmit={submit}>
      <p className="signoff-note">
        {money(payout)} is over the payout limit. A handler signs off before it
        is paid.
      </p>
      {!signedOff && (
        <>
          <label htmlFor="handler">Handler</label>
          <select
            id="handler"
            value={handlerId}
            onChange={(event) => {
              setHandlerId(event.target.value);
            }}
          >
            {handlers.map((handler) => (
              <option key={handler.handler_id} value={handler.handler_id}>
                {handler.name}
              </option>
            ))}
          </select>
        </>
      )}
      <button
        className="button"
        type="submit"
        disabled={busy || (!signedOff && !handlerId)}
      >
        {signedOff ? "Pay" : "Sign off and pay"}
      </button>
      {error && (
        <p className="pill tone-alert" role="alert">
          {error}
        </p>
      )}
    </form>
  );
}
