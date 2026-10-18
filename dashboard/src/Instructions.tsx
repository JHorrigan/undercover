import { api } from "./api";
import { useData } from "./hooks";

/** The agent's instructions, read only. */
export function Instructions() {
  const { data, error } = useData(api.instructions, 0);
  return (
    <>
      <div className="page-head">
        <h1>Agent instructions</h1>
        <span className="muted">Read only</span>
      </div>
      {error && (
        <p className="error">Couldn't load the instructions: {error}</p>
      )}
      {data && <pre className="panel instructions">{data}</pre>}
    </>
  );
}
