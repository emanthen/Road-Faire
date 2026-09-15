/** The 11 non-resident-surcharge parks, mirroring apps.fees.constants.SURCHARGE_PARK_SLUGS.
 * A static list here avoids a hard dependency on the (currently demo-seeded) spot catalog
 * for the standalone fee calculator tool. */
export const SURCHARGE_PARKS = [
  { slug: "acad", name: "Acadia" },
  { slug: "brca", name: "Bryce Canyon" },
  { slug: "ever", name: "Everglades" },
  { slug: "glac", name: "Glacier" },
  { slug: "grca", name: "Grand Canyon" },
  { slug: "grte", name: "Grand Teton" },
  { slug: "romo", name: "Rocky Mountain" },
  { slug: "seki", name: "Sequoia & Kings Canyon" },
  { slug: "yell", name: "Yellowstone" },
  { slug: "yose", name: "Yosemite" },
  { slug: "zion", name: "Zion" },
] as const;
