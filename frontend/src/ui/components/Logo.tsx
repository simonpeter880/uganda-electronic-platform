"use client";

import { usePathname } from "next/navigation";
import { LinkWithChannel } from "../atoms/LinkWithChannel";

const companyName = "Uganda Electronics";

export const Logo = () => {
	const pathname = usePathname();

	if (pathname === "/") {
		return (
			<h1 className="flex items-center font-bold text-white text-xl" aria-label="homepage">
				{companyName}
			</h1>
		);
	}
	return (
		<div className="flex items-center font-bold text-white text-xl">
			<LinkWithChannel aria-label="homepage" href="/" className="hover:text-white/90 transition-colors">
				{companyName}
			</LinkWithChannel>
		</div>
	);
};
