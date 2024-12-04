// src/components/ui/Input.tsx
import React from "react";

interface InputProps {
  value: string;
  onChange: React.ChangeEventHandler<HTMLInputElement>;
  className?: string;
  placeholder?: string;
}

const Input: React.FC<InputProps> = ({ value, onChange, className, placeholder }) => {
  return (
    <input
      type="text"
      value={value}
      onChange={onChange}
      className={`input ${className}`}
      placeholder={placeholder}
    />
  );
};

export { Input };
