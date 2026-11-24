import { useCallback, useEffect, useState } from "react";
import { message } from "./format";

/** Load data, and reload it every `everyMs` while `live` says to. */
export function useLive<T>(
  load: () => Promise<T>,
  everyMs: number,
  live: (data: T) => boolean,
) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(() => {
    load()
      .then((next) => {
        setData(next);
        setError(null);
      })
      .catch((reason: unknown) => {
        setError(message(reason));
      });
  }, [load]);

  useEffect(refresh, [refresh]);

  const keepGoing = data !== null && live(data);
  useEffect(() => {
    if (!keepGoing) return;
    const timer = setInterval(refresh, everyMs);
    return () => {
      clearInterval(timer);
    };
  }, [keepGoing, refresh, everyMs]);

  return { data, error, refresh };
}
