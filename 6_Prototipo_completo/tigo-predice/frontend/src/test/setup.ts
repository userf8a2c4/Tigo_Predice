import "@testing-library/jest-dom/vitest";

// jsdom no implementa scrollTo en elementos (lo usa el teléfono para bajar al último mensaje)
Element.prototype.scrollTo = () => {};
