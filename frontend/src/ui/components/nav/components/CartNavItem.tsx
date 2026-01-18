import { ShoppingBagIcon } from "lucide-react";
import clsx from "clsx";
import * as Checkout from "@/lib/checkout";
import { LinkWithChannel } from "@/ui/atoms/LinkWithChannel";

export const CartNavItem = async ({ channel }: { channel: string }) => {
	let lineCount = 0;

	try {
		const checkoutId = await Checkout.getIdFromCookies(channel);
		const checkout = checkoutId ? await Checkout.find(checkoutId) : null;
		lineCount = checkout ? checkout.lines.reduce((result, line) => result + line.quantity, 0) : 0;
	} catch (error) {
		// Gracefully handle cookie/checkout errors
		console.error("Cart error:", error);
	}

	return (
		<LinkWithChannel href="/cart" className="relative flex items-center hover:opacity-80 transition-opacity" data-testid="CartNavItem">
			<ShoppingBagIcon className="h-6 w-6 shrink-0 text-white" aria-hidden="true" />
			{lineCount > 0 ? (
				<div
					className={clsx(
						"absolute bottom-0 right-0 -mb-2 -mr-2 flex h-5 flex-col items-center justify-center rounded-full bg-white text-xs font-bold text-primary-500",
						lineCount > 9 ? "w-5 px-1" : "w-5",
					)}
				>
					{lineCount} <span className="sr-only">item{lineCount > 1 ? "s" : ""} in cart, view bag</span>
				</div>
			) : (
				<span className="sr-only">0 items in cart</span>
			)}
		</LinkWithChannel>
	);
};
