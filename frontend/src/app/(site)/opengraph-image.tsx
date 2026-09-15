import { ImageResponse } from "next/og";

export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default function OpengraphImage() {
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
        <div style={{ fontSize: 64, fontWeight: 600 }}>Roadfare</div>
        <div style={{ fontSize: 32, color: "#E8A33D", marginTop: 16 }}>
          Know the real cost before you book.
        </div>
      </div>
    ),
    { ...size }
  );
}
