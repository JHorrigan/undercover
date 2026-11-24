import { useEffect, useState } from "react";
import { api } from "./api";
import { message } from "./format";

export function Instructions() {
  const [text, setText] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .instructions()
      .then((instructions) => {
        setText(instructions.text);
      })
      .catch((reason: unknown) => {
        setError(message(reason));
      });
  }, []);

  return (
    <>
      <h1>The agent's instructions</h1>
      <p className="lede">
        Read only. A change is reviewed and approved before it goes live.
      </p>
      {error && (
        <p className="error">Couldn't load the instructions: {error}</p>
      )}
      {text && (
        <section className="card" aria-label="Instructions">
          <pre className="instructions">{text}</pre>
        </section>
      )}
    </>
  );
}
