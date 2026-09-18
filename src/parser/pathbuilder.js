export class PathbuilderParseError extends Error {
  constructor(message, options) {
    super(message, options);
    this.name = "PathbuilderParseError";
  }
}

export function clone(value) {
  return structuredClone(value);
}

export function parsePathbuilder(input) {
  let document;
  if (typeof input === "string") {
    try {
      document = JSON.parse(input);
    } catch (cause) {
      throw new PathbuilderParseError("Invalid Pathbuilder JSON", { cause });
    }
  } else {
    document = clone(input);
  }

  if (!document || typeof document !== "object" || Array.isArray(document)) {
    throw new PathbuilderParseError("Pathbuilder document must be an object");
  }
  if (!document.build || typeof document.build !== "object" || Array.isArray(document.build)) {
    throw new PathbuilderParseError("Pathbuilder document must contain a build object");
  }
  return document;
}
