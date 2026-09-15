import { ImageResponse } from "next/og";
import { fetchSpot } from "@/lib/api";

export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default async function Image({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const spot = await fetchSpot(slug);

  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          alignItems: "flex-start",
          justifyContent: "flex-end",
          background: "#24503F",
          color: "#FAFAF7",
          padding: 64,
        }}
      >
        <div style={{ fontSize: 56, fontWeight: 600 }}>{spot.name}</div>
        <div style={{ fontSize: 28, color: "#E8A33D", marginTop: 12 }}>Roadfare</div>
      </div>
    ),
    { ...size }
  );
}
