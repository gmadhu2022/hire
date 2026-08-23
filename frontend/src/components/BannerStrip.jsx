import { useEffect, useState, useRef } from "react";
import { api } from "../lib/api";

/**
 * Global promotional strip shown on every job-seeker page (item 4).
 * Supports HD image, GIF, video and audio; rotates when several are live.
 */
const THEMES = {
  navy: "from-navy to-navy-600",
  green: "from-brandgreen-600 to-brandgreen",
  slate: "from-slate-800 to-slate-600",
  cobalt: "from-blue-800 to-blue-600",
};

export default function BannerStrip({ audience = "jobseekers" }) {
  const [banners, setBanners] = useState([]);
  const [i, setI] = useState(0);
  const [dismissed, setDismissed] = useState(false);
  const audioRef = useRef(null);
  const [playing, setPlaying] = useState(false);

  useEffect(() => {
    api.get(`/api/public/banners?audience=${audience}`, { auth: false })
      .then(setBanners).catch(() => {});
  }, [audience]);

  useEffect(() => {
    if (banners.length < 2) return;
    const id = setInterval(() => setI((x) => (x + 1) % banners.length), 8000);
    return () => clearInterval(id);
  }, [banners.length]);

  if (dismissed || banners.length === 0) return null;
  const b = banners[i];
  const theme = THEMES[b.theme] || THEMES.navy;

  const click = () => {
    api.post(`/api/public/banners/${b.id}/click`, {}, { auth: false }).catch(() => {});
    if (b.cta_link) window.open(b.cta_link, "_blank", "noopener");
  };

  const toggleAudio = () => {
    const el = audioRef.current;
    if (!el) return;
    if (el.paused) { el.play(); setPlaying(true); } else { el.pause(); setPlaying(false); }
  };

  return (
    <div className={`no-print relative mb-5 overflow-hidden rounded-2xl bg-gradient-to-r ${theme} text-white shadow-card`}>
      <div className="flex flex-col gap-4 p-5 sm:flex-row sm:items-center">
        {/* media */}
        {b.media_url && b.media_type !== "audio" && (
          <div className="w-full shrink-0 overflow-hidden rounded-xl sm:w-56">
            {b.media_type === "video" ? (
              <video src={b.media_url} poster={b.poster_url || undefined}
                     autoPlay={b.autoplay} muted={b.muted} loop playsInline
                     className="h-32 w-full object-cover sm:h-28" />
            ) : (
              <img src={b.media_url} alt="" className="h-32 w-full object-cover sm:h-28" loading="lazy" />
            )}
          </div>
        )}

        <div className="min-w-0 flex-1">
          {b.company_name && (
            <span className="text-[11px] font-semibold uppercase tracking-wider text-white/70">
              {b.company_name}
            </span>
          )}
          <h3 className="mt-0.5 text-lg font-extrabold leading-snug">{b.title}</h3>
          {b.text_content && <p className="mt-1 text-sm text-white/85">{b.text_content}</p>}

          <div className="mt-3 flex flex-wrap items-center gap-2">
            {b.cta_label && (
              <button onClick={click}
                      className="rounded-lg bg-white px-4 py-2 text-sm font-semibold text-navy transition-transform hover:scale-[1.03]">
                {b.cta_label}
              </button>
            )}
            {b.media_type === "audio" && b.media_url && (
              <>
                <button onClick={toggleAudio}
                        className="rounded-lg border border-white/30 px-3 py-2 text-sm font-semibold hover:bg-white/10">
                  {playing ? "❚❚ Pause" : "▶ Listen"}
                </button>
                <audio ref={audioRef} src={b.media_url} onEnded={() => setPlaying(false)} />
              </>
            )}
          </div>
        </div>

        {/* rotation dots */}
        {banners.length > 1 && (
          <div className="flex gap-1.5 sm:flex-col">
            {banners.map((_, x) => (
              <button key={x} onClick={() => setI(x)}
                      className={`h-2 rounded-full transition-all ${x === i ? "w-5 bg-white sm:h-5 sm:w-2" : "w-2 bg-white/40"}`}
                      aria-label={`Banner ${x + 1}`} />
            ))}
          </div>
        )}
      </div>

      <button onClick={() => setDismissed(true)}
              className="absolute right-2 top-2 rounded-full px-2 py-0.5 text-xs text-white/60 hover:bg-white/10 hover:text-white"
              aria-label="Dismiss">×</button>
    </div>
  );
}
