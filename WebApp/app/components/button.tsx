// Name(s): William Johnson, Katie Golder
//5/5/25
//https://nextjs.org/docs/pages/building-your-application/authentication
// LoginButton.tsx
import React, { MouseEvent } from "react";
import { useRouter } from "next/navigation";

interface ButtonProps {
  text: string;
  link?: string;
  handleButton?: (event: MouseEvent<HTMLButtonElement>) => void;
}

const Button: React.FC<ButtonProps> = ({ text, link, handleButton }) => {
  const router = useRouter();

  function handleClick(event: MouseEvent<HTMLButtonElement>) {
    event.preventDefault();

    if (handleButton) {
      handleButton(event);
    } else if (link) {
      router.push(link);
    } else {
      // Optionally log or warn
      console.warn("No link or handler provided.");
    }
  }

  return (
    <button
      className="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 capitalize"
      onClick={handleClick}
    >
      {text}
    </button>
  );
};

export default Button;
