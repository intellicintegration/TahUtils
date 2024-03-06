/********************************************************************************
 * Copyright (c) 2017, 2018 Cirrus Link Solutions and others
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License 2.0 which is available at
 * http://www.eclipse.org/legal/epl-2.0.
 *
 * SPDX-License-Identifier: EPL-2.0
 *
 * Contributors:
 *   Cirrus Link Solutions - initial implementation
 ********************************************************************************/

import * as sparkplugbpayload from './lib/sparkplugbpayload';

export function get(namespace: string | undefined | null) {
    if (namespace !== undefined && namespace !== null) {
        if (namespace === "spBv1.0") {
            return sparkplugbpayload;
        }
    }
    return null;
};
