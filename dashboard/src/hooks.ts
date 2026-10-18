import { useCallback, useEffect, useState } from "react";

export type Route =
  { page: "queue" } | { page: "claim"; id: string } | { page: "instructions" };

export function parseRoute(hash: string): Route {
  const claim = /^#\/claims\/([\w-]+)$/.exec(hash);
  if (claim?.[1]) return { page: "claim", id: claim[1] };
  if (hash === "#/instructions") return { page: "instructions" };
  return { page: "queue" };
}

export function useRoute(): Route {
  const [route, setRoute] = useState(() => parseRoute(window.location.hash));
  useEffect(() => {
    const onChange = () => {
      setRoute(parseRoute(window.location.hash));
    };
    window.addEventListener("hashchange", onChange);
    return () => {
      window.removeEventListener("hashchange", onChange);
    };
  }, []);
  return route;
}

export interface Loaded<T> {
  data: T | undefined;
  error: string | undefined;
  reload: () => void;
}

/** Load data on mount, and again every refreshMs when it is above zero. */
export function useData<T>(
  load: () => Promise<T>,
  refreshMs: number,
): Loaded<T> {
  const [data, setData] = useState<T>();
  const [error, setError] = useState<string>();
  const reload = useCallback(() => {
    load().then(
      (value) => {
        setData(value);
        setError(undefined);
      },
      (reason: unknown) => {
        setError(reason instanceof Error ? reason.message : String(reason));
      },
    );
  }, [load]);
  useEffect(() => {
    reload();
    if (refreshMs <= 0) return;
    const timer = setInterval(reload, refreshMs);
    return () => {
      clearInterval(timer);
    };
  }, [reload, refreshMs]);
  return { data, error, reload };
}
